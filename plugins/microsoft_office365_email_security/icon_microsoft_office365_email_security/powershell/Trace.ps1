param (
    [string]$Username = "",
    [string]$Password = "",
    [string]$Sender,
    [string]$StartDate, 
    [string]$EndDate
)

if ($StartDate.Length -eq 0) {
    throw "Start Date is required"
}

if ($EndDate.Length -eq 0) {
    throw "End Date is required"
}

if ($Sender.Length -eq 0) {
    throw "Sender is required"
}

$timeout = New-TimeSpan -Minutes 60
$stopwatch = [diagnostics.stopwatch]::StartNew()

#imports and connect
. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection.ps1 -Username $Username -Password $Password

$out = $null # dummy var for output we don't really want

$result = $null #initialize for [ref]
Exec-Retry 'Get-MessageTraceV2 -SenderAddress $Sender -StartDate $StartDate -EndDate $EndDate -ErrorAction Stop| Select-Object -Property * | ConvertTo-Json -AsArray -compress' ([ref]$result)

write-host "Success - trace follows:"
Write-Host ($result)
Disconnect-ExchangeOnline -Confirm:$false
