param (
    [string]$Username,
    [string]$Password
)

if ($Username.Length -eq 0) {
    throw "Username is required."
}

if ($Password.Length -eq 0) {
    throw "Password is required."
}
else {
    $SecPassword = ConvertTo-SecureString -String $Password -AsPlainText -Force
    $o365cred = New-Object System.Management.Automation.PSCredential ($Username, $SecPassword)
}

#import util functions
. $PSScriptRoot/RetryUtil.ps1

# suppress the progress bars
$ProgressPreference = "SilentlyContinue"
Write-Host "IPPSSession attempting..."

# catch our connection exception and check if it's MI_RESULT_FAILED, and use a longer timeout if so
$Connection = $null
try {
  Exec-Retry 'Disconnect-ExchangeOnline -Confirm:$false; Connect-IPPSSession -Credential $o365cred -EnableSearchOnlySession' -output ([ref]$Connection)
}catch{
  Write-Host "Something went wrong"
  Write-Host $_.Exception
  if($_.Exception|Select-String "MI_RESULT_FAILED" -CaseSensitive){
    write-warning $_.Exception
    Exec-Retry 'Disconnect-ExchangeOnline -Confirm:$false; Connect-IPPSSession -Credential $o365cred -EnableSearchOnlySession' -output ([ref]$Connection) -tries 2
  } else {
    write-host $_.Exception
    throw $_.Exception
  }
}
