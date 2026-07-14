param (
    [string]$Username = "",
    [string]$Password = ""
)

. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection.ps1 -Username $Username -Password $Password

$out = $null

$result = $null
Exec-Retry 'Get-HostedContentFilterPolicy | Select-Object -Property Name, DistinguishedName, Guid, BlockedSenderDomains | ConvertTo-Json -AsArray -compress' ([ref]$result)

write-host "Success - trace follows:"
Write-Host ($result)
Disconnect-ExchangeOnline -Confirm:$false