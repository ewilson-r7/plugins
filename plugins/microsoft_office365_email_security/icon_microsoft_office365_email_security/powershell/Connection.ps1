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

# catch our connection exception and check if it's MI_RESULT_FAILED, and use a longer timeout if so
$Connection = $null
try {
  Exec-Retry 'Disconnect-ExchangeOnline -Confirm:$false; Connect-ExchangeOnline -Credential $o365cred' -output ([ref]$Connection)
}catch{
  if($_.Exception|Select-String "MI_RESULT_FAILED" -CaseSensitive){
    write-warning $_.Exception
    Exec-Retry 'Disconnect-ExchangeOnline -Confirm:$false; Connect-ExchangeOnline -Credential $o365cred' -output ([ref]$Connection)  -tries 2
  } else {
    write-host $_.Exception
    throw $_.Exception
  }
}


$ConnectionTest = $null
try{
    Exec-Retry 'Get-ConnectionInformation' `
([ref]$ConnectionTest)
    if($ConnectionTest){
        Write-Host "Connection was successful."
    } else {
        throw "Connection not established, please check credentials and try again."
    }
}catch{
    write-host $_.Exception
    throw $_.Exception
}
