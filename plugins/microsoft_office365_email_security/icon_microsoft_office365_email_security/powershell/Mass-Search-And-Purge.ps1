<#
.SYNOPSIS
    This script executes the mass delete functionality of the Office 365 Security and Compliance application. The script makes use of the Policy and Compliance Content Search actions exposed by Office 365. More information is available here:
    https://docs.microsoft.com/en-us/powershell/module/exchange/policy-and-compliance-content-search/new-compliancesearchaction?view=exchange-ps

.DESCRIPTION
    The Mass-Delete script finds all the e-mails in your organization based on the search criteria you give it and deletes them.

    The known limitations of this script are a maximum of 10 items per mailbox and a limit of 50,000 mailboxes in an organization. For help with large organizations follow this link: https://docs.microsoft.com/en-us/office365/securitycompliance/search-for-and-delete-messages-in-your-organization

    Un-indexed items cannot be removed from mailboxes using this script.

.PARAMETER Username
	Username with administrative rights to Office 365

.PARAMETER Password
	Securestring password

.PARAMETER ComplianceSearchName
	The name of the compliance search used to find content to delete

.PARAMETER ContentMatchQuery
	This parameter uses a text search string or a query that's formatted by using the Keyword Query Language (KQL). For more information about KQL, see Keyword Query Language syntax reference (https://go.microsoft.com/fwlink/p/?linkid=269603).

.PARAMETER TimeoutInMinutes
	OPTIONAL: Default 60: The length in minutes after which the script terminates. The timeout resets after a successful search and is applied again to the delete action. 

.PARAMETER DeleteItems
	OPTIONAL: Default $false: The script only executes the delete action if this parameter is $true.  The default value of $false allows configuration debugging without accidentally deleting content. 

.PARAMETER Office365URI
	OPTIONAL: Default https://ps.compliance.protection.outlook.com/powershell-liveid/: This parameter sets the location of the Office 365 or on-premise exchange server from which to execute the compliance actions.

.EXAMPLE
    Mass-Delete -Username someuser@microsoft.com -Password password -ComplianceSearchName "Content Search" -ContentMatchQuery subject:"Phishy"

.LINK
    https://www.rapid7.com/
#>

param (
    [string]$Username = "",
    [string]$Password = "",
    [string]$ComplianceSearchName,
    [string]$ContentMatchQuery,
    [Int32]$TimeoutInMinutes = 60, 
    [string]$DeleteItems = $false
)

if($ComplianceSearchName.Length -eq 0){
    throw "ComplianceSearchName is required"
}

if($ContentMatchQuery.Length -eq 0){
    throw "ContentMatchQuery is required. For more information go to https://docs.microsoft.com/en-us/sharepoint/dev/general-development/keyword-query-language-kql-syntax-reference."
}

#creating the variables so I can pass as a ref to the abstract commands
$result = $null
$deleteJobStatus = $null
$deleteJobDetails = $null
$searchJobDetails = $null
$searchResults = $null
$out = $null #dummy for when we don't really want the output

# Convert input string to a boolean (to avoid a spec change)
[System.Convert]::ToBoolean($DeleteItems)

#start timer for timeout (useful impl. with actual timer- subcommands may run for a while, we want total time)
$timeout = New-TimeSpan -Minutes $TimeoutInMinutes
$stopwatch = [diagnostics.stopwatch]::StartNew()

#import util functions and establish connections
. $PSScriptRoot/RetryUtil.ps1
. $PSScriptRoot/Connection-IPPSSession.ps1 -Username $Username -Password $Password
$out = $null # dummy var for output we don't really want

$cmd = 'Remove-ComplianceSearch -Identity $ComplianceSearchName -Confirm:$false -ErrorAction SilentlyContinue'
Exec-Retry $cmd ([ref]$out) # cleanup (leaving the ComplianceSearchAction now, for blame reasons)

#create the compliance Search
Write-Host "Creating Search..."
$cmd = 'New-ComplianceSearch -Name $ComplianceSearchName -ExchangeLocation ''All'' -AllowNotFoundExchangeLocationsEnabled $true -ContentMatchQuery $ContentMatchQuery -Force -ErrorAction Stop'
Exec-Retry $cmd ([ref]$searchJobDetails)
#Start the compliance Search
Exec-Retry 'Start-ComplianceSearch -Identity $ComplianceSearchName -Force -ErrorAction Stop' ([ref]$out)
Write-Host "Search Created."
Write-Host "Running Search..."

# loop until search results are ready, waiting every 10 seconds
# check on search results until they are completed
while($searchResults.status -ne "Completed"){
    Write-Host -NoNewline "."
    try {
        Exec-Retry 'Get-ComplianceSearch -Identity $ComplianceSearchName -ErrorAction Stop' ([ref]$searchResults) 1
    } catch {
        # handle errors that should be fatal here - swallow the error for now
        write-host "Retry Exec Bailed in Results Loop - Continuing."
    }    

    if($stopwatch.elapsed -gt $timeout){
        Disconnect-ExchangeOnline -Confirm:$false
        throw "Timeout was exceeded."
    }
    Start-Sleep -Seconds 10       
}
Write-Output "Search Completed."


Write-Output "Resetting timeout, attempting to delete."
$timeout = New-TimeSpan -Minutes $TimeoutInMinutes
$stopwatch = [diagnostics.stopwatch]::StartNew()

# run delete action then loop to check for completion
if($DeleteItems -eq $true){
    Write-Host "Deleting..."
    $cmd = 'New-ComplianceSearchAction -SearchName $ComplianceSearchName -Purge -PurgeType SoftDelete -Confirm:$false -ErrorAction Stop'
    Exec-Retry $cmd ([ref]$deleteJobDetails)

    $Identity = $deleteJobDetails.JobRunId # to lookup completion of Job (UID)
    while($deleteJobStatus.status -ne "Completed"){
        try {
            Exec-Retry 'Get-ComplianceSearchAction -Identity $Identity -ErrorAction Stop' ([ref]$deleteJobStatus) 1
        } catch {
            # handle errors that should be fatal here - swallow the error for now
            Write-Host "Retry Exec Bailed in Wait for Delete To Complete - Ignoring."
        }
        if($stopwatch.elapsed -gt $timeout){
            Disconnect-ExchangeOnline -Confirm:$false
            throw "Timeout was exceeded."
        }

        Start-Sleep -Seconds 10
        # Purge action completed- report success for the action to see
        Write-Output "Success!"
    }
}
else{
    Write-Host "DeleteItems was set to false. Delete step was skipped."
    Write-Output "Success!"
}

Write-Output "Script Complete"

Disconnect-ExchangeOnline -Confirm:$false
