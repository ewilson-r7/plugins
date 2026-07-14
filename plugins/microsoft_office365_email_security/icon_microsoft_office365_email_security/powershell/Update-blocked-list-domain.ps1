param (
    [string]$Username = "",
    [string]$Password = "",
    [string]$SearchFilter,
    [string]$Action,
    [string]$Domains,
    [Int32]$TimeoutInMinutes = 60
)

$updateJobStatus = $null
$updateJobDetails = $null

$timeout = New-TimeSpan -Minutes $TimeoutInMinutes

. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection.ps1 -Username $Username -Password $Password

$out = $null

$stopwatch = [diagnostics.stopwatch]::StartNew()

[string[]]$arrayOfDomains = $Domains.Replace('"','').Split(',')
$Action = $Action.Replace('"','')
if ($Action -eq "Add") {
    write-output "Add"
    Exec-Retry 'Set-HostedContentFilterPolicy -Identity $SearchFilter -BlockedSenderDomains @{Add=$arrayOfDomains}' ([ref]$updateJobDetails)
}
elseif ($Action -eq "Remove") {
    write-output "Remove"
    Exec-Retry 'Set-HostedContentFilterPolicy -Identity $SearchFilter -BlockedSenderDomains @{Remove=$arrayOfDomains}' ([ref]$updateJobDetails)
}

if($null -ne $updateJobDetails){
    $Identity = $updateJobDetails.JobRunId
    while($updateJobStatus.status -ne "Completed"){
        Write-Host -NoNewline "."
        try {
            Exec-Retry "Get-ComplianceSearchAction -Identity $Identity -ErrorAction Stop" ([ref]$updateJobStatus) 1
        } catch {
            Write-Host "Error thrown in poll for delete status loop - Ignoring."
        }

        if($stopwatch.elapsed -gt $timeout){
            Disconnect-ExchangeOnline -Confirm:$false
            throw "Timeout was exceeded."
        }
        Start-Sleep -Seconds 10
    }
}

Write-Output "Success"
Disconnect-ExchangeOnline -Confirm:$false
