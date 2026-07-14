param (
    [string]$Username = "",
    [string]$Password = "",
    [string]$ComplianceSearchName,
    [string]$ContentMatchQuery,
    [Int32]$TimeoutInMinutes = 60,
    [string]$ExchangeLocation = "All"
)

if ($ComplianceSearchName.Length -eq 0) {
    throw "ComplianceSearchName is required"
}

if ($ContentMatchQuery.Length -eq 0) {
    throw "ContentMatchQuery is required. For more information go to https://docs.microsoft.com/en-us/sharepoint/dev/general-development/keyword-query-language-kql-syntax-reference."
}

if ($ExchangeLocation.Length -eq 0) {
    ExchangeLocation = 'All'
}
$ExchangeLocations = $ExchangeLocation -split ','
$ExchangeLocationsClean = $ExchangeLocations | % { $_.Trim()}

$timeout = New-TimeSpan -Minutes $TimeoutInMinutes
$stopwatch = [diagnostics.stopwatch]::StartNew()
$searchJobDetails = $null
$searchResults = $null
$out = $null # dummy var for output we don't really want

. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection-IPPSSession.ps1 -Username $Username -Password $Password

$cmd = 'Remove-ComplianceSearch -Identity $ComplianceSearchName -Confirm:$false -ErrorAction SilentlyContinue'
Exec-Retry $cmd ([ref]$out) # cleanup (leaving the ComplianceSearchAction now, for blame reasons)

Write-Output " "
Write-Host "Exchange Location set to: " $ExchangeLocationsClean
Write-Output " "
Write-Host "Creating Search..."

$cmd = 'New-ComplianceSearch -Name $ComplianceSearchName -ExchangeLocation $ExchangeLocationsClean -AllowNotFoundExchangeLocationsEnabled $true -ContentMatchQuery $ContentMatchQuery -Force -ErrorAction Stop'
Exec-Retry $cmd ([ref]$searchJobDetails)

# Start the compliance Search
Write-Output " "
Write-Host "Running Search..."
Exec-Retry 'Start-ComplianceSearch -Identity $ComplianceSearchName -Force -ErrorAction Stop' ([ref]$out)
Write-Host "Start-ComplianceSearch output:"

# loop until search results are ready, waiting every 10 seconds
# check on search results until they are completed
$searchResults = $null
while($searchResults.status -ne "Completed"){
    Write-Host -NoNewline "."
    try {
        Exec-Retry 'Get-ComplianceSearch -Identity $ComplianceSearchName' ([ref]$searchResults) 1
    } catch {
        # handle errors that should be fatal here - swallow all for now
        Write-Host "Error thrown in Results Polling Loop - Ignoring."
    }

    if($stopwatch.elapsed -gt $timeout){
        Disconnect-ExchangeOnline -Confirm:$false
        throw "Timeout was exceeded."
    }
    Start-Sleep -Seconds 10
}
Write-Output "Search Completed."
Disconnect-ExchangeOnline -Confirm:$false

Write-Host ($searchResults | Select-Object -Property "SearchStatistics")
