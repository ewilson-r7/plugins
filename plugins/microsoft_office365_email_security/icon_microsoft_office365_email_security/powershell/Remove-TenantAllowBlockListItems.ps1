param (
    [string]$Username = "",
    [string]$Password = "",
    [string]$ListType = "",
    [string]$Entries = ""
)

if ($ListType.Length -eq 0) {
    throw "ListType is required (Sender, Url, FileHash, or IP)"
}

if ($Entries.Length -eq 0) {
    throw "Entries is required"
}

. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection.ps1 -Username $Username -Password $Password

$out = $null

# Parse the comma-separated entries into an array
[string[]]$entryArray = $Entries.Replace('"', '').Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_.Length -gt 0 }

$cmd = 'Remove-TenantAllowBlockListItems -ListType $ListType -Entries $entryArray -ErrorAction Stop'

Exec-Retry $cmd ([ref]$out)

Write-Output "Success"
Disconnect-ExchangeOnline -Confirm:$false
