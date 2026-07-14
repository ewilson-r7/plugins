param (
    [string]$Username = "",
    [string]$Password = "",
    [string]$ComplianceSearchName,
    [Int32]$TimeoutInMinutes = 60
)

if($ComplianceSearchName.Length -eq 0){
    throw "ComplianceSearchName is required"
}

$timeout = New-TimeSpan -Minutes $TimeoutInMinutes

$deleteJobStatus = $null # status of the action
$deleteJobDetails = $null # details about the action

#import util functions and establish connections
. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection-IPPSSession.ps1 -Username $Username -Password $Password

$out = $null # dummy var for output we don't really want
$searchStatus = $null

# Verify the compliance search exists and has completed before attempting purge
Write-Host "Checking compliance search status..."
try {
    Exec-Retry 'Get-ComplianceSearch -Identity $ComplianceSearchName -ErrorAction Stop' ([ref]$searchStatus) 1
} catch {
    Disconnect-ExchangeOnline -Confirm:$false
    throw "Compliance search '$ComplianceSearchName' not found or could not be retrieved. Error: $_"
}

if ($searchStatus.Status -ne "Completed") {
    Disconnect-ExchangeOnline -Confirm:$false
    throw "Compliance search '$ComplianceSearchName' has not completed. Current status: $($searchStatus.Status). Please wait for the search to finish before running purge."
}

if ($searchStatus.Items -eq 0) {
    Disconnect-ExchangeOnline -Confirm:$false
    throw "Compliance search '$ComplianceSearchName' returned 0 results. Nothing to purge. Verify the search query is correct and the search has completed successfully."
}

Write-Host "Search '$ComplianceSearchName' completed with $($searchStatus.Items) item(s). Proceeding with purge."

$stopwatch = [diagnostics.stopwatch]::StartNew()

Write-Host -NoNewline "Deleting..."

# Creates and runs Purge action
$cmd = 'New-ComplianceSearchAction -SearchName $ComplianceSearchName -Purge -PurgeType SoftDelete -Confirm:$false -ErrorAction Stop'
Exec-Retry $cmd ([ref]$deleteJobDetails)

# loops and checks the action results until it is completed
if($null -ne $deleteJobDetails){
    $Identity = $deleteJobDetails.JobRunId # UID of the action
    if ($null -eq $Identity) {
        Disconnect-ExchangeOnline -Confirm:$false
        throw "Purge action was created but returned no JobRunId. Cannot poll for completion."
    }
    $terminalFailureStates = @("Failed", "Stopped", "PartiallySucceeded")
    while($deleteJobStatus.status -ne "Completed"){
        Write-Host -NoNewline "."
        try {
            Exec-Retry "Get-ComplianceSearchAction -Identity $Identity -ErrorAction Stop" ([ref]$deleteJobStatus) 1
        } catch {
            # swallow transient poll errors; terminal failure states are handled below
            Write-Host "Error thrown in poll for delete status loop - Ignoring."
        }

        if ($deleteJobStatus.status -in $terminalFailureStates) {
            Disconnect-ExchangeOnline -Confirm:$false
            throw "Purge action failed with status: $($deleteJobStatus.status). Results: $($deleteJobStatus.Results)"
        }

        if($stopwatch.elapsed -gt $timeout){
            Disconnect-ExchangeOnline -Confirm:$false
            throw "Timeout was exceeded."
        }
        Start-Sleep -Seconds 10
    }
}
Write-Output "Script Complete"
Disconnect-ExchangeOnline -Confirm:$false
