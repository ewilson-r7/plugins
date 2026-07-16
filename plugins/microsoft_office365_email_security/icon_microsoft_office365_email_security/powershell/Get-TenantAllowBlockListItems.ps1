param (
    [string]$Username = "",
    [string]$Password = "",
    [string]$ListType = "",
    [string]$ActionType = ""
)

if ($ListType.Length -eq 0) {
    throw "ListType is required (Sender, Url, FileHash, or IP)"
}

. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection.ps1 -Username $Username -Password $Password

$result = $null
$cmd = 'Get-TenantAllowBlockListItems -ListType $ListType'

if ($ActionType -eq "Allow") {
    $cmd += ' -Allow'
}
elseif ($ActionType -eq "Block") {
    $cmd += ' -Block'
}

$cmd += ' -ErrorAction Stop | Select-Object -Property Identity, Value, Action, ListType, ExpirationDate, Notes, LastModifiedDateTime, CreatedDateTime | ConvertTo-Json -AsArray -Compress'

Exec-Retry $cmd ([ref]$result)

Write-Host "Success - trace follows:"
Write-Host ($result)
Disconnect-ExchangeOnline -Confirm:$false
