param (
    [string]$Username = "",
    [string]$Password = "",
    [string]$EmailOrDomainToBlock = "",
    [string]$RuleName = "InsightConnect Block List"
)

# Import util functions and establish connections
. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection.ps1 -Username $Username -Password $Password

Write-Host "Attempting to block: $($EmailOrDomainToBlock)"
Write-Host "In Transport Rule: $($RuleName)"

$out = $null # dummy var for output we don't really want
$CurrentRule = $null

# Try to retrieve the current transport rule object
Exec-Retry "Get-TransportRule -Identity `"$RuleName`" -ErrorAction SilentlyContinue" ([ref]$CurrentRule)

# Detect email vs domain
function IsEmail ($value) {
    return $value -match '^[^@\s]+@[^@\s]+\.[^@\s]+$'
}

function IsDomain ($value) {
    return $value -match '^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' -and ($value -notmatch "@")
}

# Normalize input
$value = $EmailOrDomainToBlock.Trim().ToLower()

if (!(IsEmail $value) -and !(IsDomain $value)) {
    Write-Host "ERROR: Input is neither a valid email nor a valid domain."
    Disconnect-ExchangeOnline -Confirm:$false
    exit 1
}

if ($null -ne $CurrentRule) {

    Write-Host "Rule exists. Updating..."

    # Load existing lists, ensure ArrayList form
    [System.Collections.ArrayList]$EmailList = @()
    if ($CurrentRule.FromAddressContainsWords) {
        $CurrentRule.FromAddressContainsWords | ForEach-Object {
            if ($_){ $EmailList.Add($_.ToLower()) | Out-Null }
        }
    }

    [System.Collections.ArrayList]$DomainList = @()
    if ($CurrentRule.SenderDomainIs) {
        $CurrentRule.SenderDomainIs | ForEach-Object {
            if ($_){ $DomainList.Add($_.ToLower()) | Out-Null }
        }
    }

    # Add to correct list
    if (IsEmail $value) {
        if ($EmailList -contains $value) {
            Write-Host "Email already blocked: $value"
            Disconnect-ExchangeOnline -Confirm:$false
            exit 0
        }
        $EmailList.Add($value) | Out-Null
        Write-Host "Added email to block list: $value"
    }
    elseif (IsDomain $value) {
        if ($DomainList -contains $value) {
            Write-Host "Domain already blocked: $value"
            Disconnect-ExchangeOnline -Confirm:$false
            exit 0
        }
        $DomainList.Add($value) | Out-Null
        Write-Host "Added domain to block list: $value"
    }

    # Command length handling (Exchange limit ~8192 chars)
    function Get-CommandLength {
        param($Emails, $Domains)
        $cmd = "Set-TransportRule -Identity $RuleName -SenderDomainIs $($Domains -join ',') -FromAddressContainsWords $($Emails -join ',')"
        return $cmd.Length
    }

    while ((Get-CommandLength -Emails $EmailList -Domains $DomainList) -gt 8100) {
        if ($EmailList.Count -gt 0) {
            Write-Host "Pruning oldest EMAIL entry: $($EmailList[0])"
            $EmailList.RemoveAt(0)
        }
        elseif ($DomainList.Count -gt 0) {
            Write-Host "Pruning oldest DOMAIN entry: $($DomainList[0])"
            $DomainList.RemoveAt(0)
        }
        else {
            break
        }
    }

    # Update the transport rule
    Exec-Retry {
        Set-TransportRule -Identity $RuleName `
            -SenderDomainIs $DomainList `
            -FromAddressContainsWords $EmailList `
            -DeleteMessage $true `
            -RejectMessageReasonText $null `
            -ErrorAction Stop `
            -RejectMessageEnhancedStatusCode $null
    } ([ref]$out)

}
else {

    # Rule does not exist, create a new one
    Write-Host "Rule does not exist. Creating a new one..."

    $CreateArgs = @{
        Name                      = $RuleName
        Comments                  = $RuleName
        Priority                  = 0
        Enabled                   = $true
        DeleteMessage             = $true
        ErrorAction               = 'Stop'
    }

    if (IsEmail $value) {
        $CreateArgs["FromAddressContainsWords"] = $value
    }
    else {
        $CreateArgs["SenderDomainIs"] = $value
    }

    Exec-Retry {
        New-TransportRule @CreateArgs
    } ([ref]$out)
}

Write-Output "Blocking finished"
Disconnect-ExchangeOnline -Confirm:$false
