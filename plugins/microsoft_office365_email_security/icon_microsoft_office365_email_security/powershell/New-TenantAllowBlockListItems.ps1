param (
    [string]$Username = "",
    [string]$Password = "",
    [string]$ListType = "",
    [string]$Entries = "",
    [string]$ActionType = "",
    [string]$NoExpiration = "false",
    [Int32]$ExpirationDays = 30,
    [string]$Notes = ""
)

if ($ListType.Length -eq 0) {
    throw "ListType is required (Sender, Url, FileHash, or IP)"
}

if ($Entries.Length -eq 0) {
    throw "Entries is required"
}

if ($ActionType.Length -eq 0) {
    throw "ActionType is required (Allow or Block)"
}

. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection.ps1 -Username $Username -Password $Password

$result = $null

# Parse the comma-separated entries into an array
[string[]]$entryArray = $Entries.Replace('"', '').Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_.Length -gt 0 }

# Build the command
$cmd = 'New-TenantAllowBlockListItems -ListType $ListType -Entries $entryArray'

if ($ActionType -eq "Allow") {
    $cmd += ' -Allow'
}
elseif ($ActionType -eq "Block") {
    $cmd += ' -Block'
}

# Handle expiration
if ($NoExpiration -eq "true") {
    $cmd += ' -NoExpiration'
}
else {
    $expirationDate = (Get-Date).AddDays($ExpirationDays).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $cmd += " -ExpirationDate `"$expirationDate`""
}

# Add notes if provided
if ($Notes.Length -gt 0) {
    $cmd += " -Notes `"$Notes`""
}

$cmd += ' -ErrorAction Stop | Select-Object -Property Identity, Value, Action, ListType, ExpirationDate, Notes, LastModifiedDateTime, CreatedDateTime | ConvertTo-Json -AsArray -Compress'

Exec-Retry $cmd ([ref]$result)

Write-Host "Success - entries follow:"
Write-Host ($result)
Disconnect-ExchangeOnline -Confirm:$false
