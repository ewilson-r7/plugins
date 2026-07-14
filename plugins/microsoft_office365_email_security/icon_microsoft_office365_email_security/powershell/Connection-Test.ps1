param (
    [string]$Username = "",
    [string]$Password = ""
)

. $PSScriptRoot/Connection.ps1 -Username $Username -Password $Password

Disconnect-ExchangeOnline -Confirm:$false

Write-Host "Connected successfully"
