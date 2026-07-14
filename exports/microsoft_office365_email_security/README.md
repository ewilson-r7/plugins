# Description

The Microsoft Office 365 email security plugin adds utilities to help administrators manage their Office 365 instances. This plugin will allow administrators to take remediation actions across their organization

# Key Features

* Block senders by domain or email address
* Search for and optionally delete email across an organization
* Get email trace information
* Manage entries in the Tenant Allow/Block List

# Requirements

* An administrative account with modern authentication enabled
* Powershell connectivity to the Office 365 cloud servers
* For more information on these requirements and setup please see the Connect to Security & Compliance PowerShell reference at the end of this document

Roles required for the action to work:
* Block Sender Transport Rule action
* Transport Rules role
* Email Compliance Search action
* Mailbox Search role
* Email Compliance Purge action
* Mailbox Import Export role
* Email Compliance Search and Purge action
* Mailbox Import Export role
* Mailbox Search role
* Message Trace action
* Message Tracking role
* Tenant Allow/Block List actions
* Tenant AllowBlockList Manager role

# Supported Product Versions

* Microsoft Office 365 2026-07-14

# Documentation

## Setup

The connection configuration accepts the following parameters:  

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|credentials|credential_username_password|None|True|Username and password|None|{"username": "user@example.com", "password": "mypassword"}|None|None|

Example input:

```
{
  "credentials": {
    "password": "mypassword",
    "username": "user@example.com"
  }
}
```

## Technical Details

### Actions


#### Block Sender Transport Rule

This action is used to add a domain or email address to a blocking transport rule in Exchange Admin Center. In Office 
365 cloud, transport rules are limited to 8k of data or roughly 8100 characters. This is roughly 400 email addresses. If
 a new email address is added (that would break that limit), existing emails would need to be manually deleted to make 
room for new additions

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|domain_or_email_to_block|string|None|True|Domain or email address to block|None|example.com|None|None|
|transport_rule_name|string|InsightConnect Block List|True|Name of transport rule|None|InsightConnect Block List|None|None|
  
Example input:

```
{
  "domain_or_email_to_block": "example.com",
  "transport_rule_name": "InsightConnect Block List"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|result|string|True|Result|Success|
  
Example output:

```
{
  "result": "Success"
}
```

#### Create Tenant Allow/Block List Entry

This action is used to add a new entry to the Tenant Allow/Block List to block or allow senders, URLs, file hashes, or 
IPs

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|action_type|string|None|True|Whether to create an allow or block entry|["Allow", "Block"]|Block|None|None|
|entries|[]string|None|True|Values to add to the list. For Sender use email or domain, for URL use the URL value, for FileHash use SHA256 hashes, for IP use IPv6 addresses or CIDR ranges|None|["evil@example.com", "malicious-domain.com"]|evil@example.com, malicious-domain.com|None|
|expiration_days|integer|30|False|Number of days until the entry expires (default 30 if no_expiration is false). Ignored if no_expiration is true|None|30|None|None|
|list_type|string|None|True|The type of entry to create|["Sender", "Url", "FileHash", "IP"]|Sender|None|None|
|no_expiration|boolean|False|False|If true, the entry will never expire. Only valid for block entries|None|False|None|None|
|notes|string|None|False|Optional notes to associate with the entry|None|Blocked due to phishing campaign|Blocked due to phishing campaign|None|
  
Example input:

```
{
  "action_type": "Block",
  "entries": [
    "evil@example.com",
    "malicious-domain.com"
  ],
  "expiration_days": 30,
  "list_type": "Sender",
  "no_expiration": false,
  "notes": "Blocked due to phishing campaign"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|entries|[]tenant_allow_block_list_entry|True|The created Tenant Allow/Block List entries|[{"Identity": "RgAAAAAI8gSyOVN1GYaKkFe7hRJnBwA87CsZ-sample", "Value": "evil@example.com", "Action": "Block", "ListType": "Sender", "ExpirationDate": "2026-08-14T00:00:00Z", "Notes": "Blocked due to phishing campaign", "LastModifiedDateTime": "2026-07-14T12:00:00Z", "CreatedDateTime": "2026-07-14T12:00:00Z"}]|
|success|boolean|True|Whether the entries were created successfully|True|
  
Example output:

```
{
  "entries": [
    {
      "Action": "Block",
      "CreatedDateTime": "2026-07-14T12:00:00Z",
      "ExpirationDate": "2026-08-14T00:00:00Z",
      "Identity": "RgAAAAAI8gSyOVN1GYaKkFe7hRJnBwA87CsZ-sample",
      "LastModifiedDateTime": "2026-07-14T12:00:00Z",
      "ListType": "Sender",
      "Notes": "Blocked due to phishing campaign",
      "Value": "evil@example.com"
    }
  ],
  "success": true
}
```

#### Email Compliance Search

This action is used to create a compliance search for provided email

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|compliance_search_name|string|None|True|Name of compliance search|None|InsightConnect Compliance Search|None|None|
|content_match_query|string|None|True|This parameter uses a text search string or a query that's formatted by using the Keyword Query Language (KQL). For more information about KQL, see Keyword Query Language syntax reference (https://go.microsoft.com/fwlink/p/?linkid=269603)|None|from:example AND subject:"Click Me!"|None|None|
|exchange_location|string|All|False|Exchange location to limit this search to. An Exchange Location can be a mailbox, group mailbox, or 'All'. If this is ommitted it will be set to All|None|user@example.com, user2@example.com|None|None|
|query_timeout|integer|60|False|Query timeout in minutes|None|60|None|None|
  
Example input:

```
{
  "compliance_search_name": "InsightConnect Compliance Search",
  "content_match_query": "from:example AND subject:\"Click Me!\"",
  "exchange_location": "All",
  "query_timeout": 60
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|affected_users|integer|True|Number of affected users|1|
|emails_found|integer|True|Emails found that matched|4|
|users|[]string|True|Email address of all affected users|["user1@example.com", "user2@example.com"]|
  
Example output:

```
{
  "affected_users": 1,
  "emails_found": 4,
  "users": [
    "user1@example.com",
    "user2@example.com"
  ]
}
```

#### Get List of Blocked Domains

This action is used to return spam filter policies in your cloud based organization

##### Input
  
*This action does not contain any inputs.*

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|spam_policy|[]spam_policy|True|Information about blocked sender domain|[ { "BlockedSenderDomains": [ "example.com" ], "DistinguishedName": "CN=Default,CN=Hosted Content Filter,CN=Transport Settings,CN=Configuration,CN=example.com,CN=ConfigurationUnits,DC=NAMPR12A004,DC=PROD,DC=OUTLOOK,DC=COM", "Guid": "9a5bb292-d659-4ac2-ac72-f6127c82189b", "Name": "Default" }, { "BlockedSenderDomains": [ "hacky.com" ], "DistinguishedName": "CN=Domain Block List,CN=Hosted Content Filter,CN=Transport Settings,CN=Configuration,CN=example.com,CN=ConfigurationUnits,DC=NAMPR12A004,DC=PROD,DC=OUTLOOK,DC=COM", "Guid": "fe557a1b-e0fa-4c13-8674-c4da30a8e884", "Name": "Domain Block List" } ]|
  
Example output:

```
{
  "spam_policy": [
    {
      "BlockedSenderDomains": [
        "example.com"
      ],
      "DistinguishedName": "CN=Default,CN=Hosted Content Filter,CN=Transport Settings,CN=Configuration,CN=example.com,CN=ConfigurationUnits,DC=NAMPR12A004,DC=PROD,DC=OUTLOOK,DC=COM",
      "Guid": "9a5bb292-d659-4ac2-ac72-f6127c82189b",
      "Name": "Default"
    },
    {
      "BlockedSenderDomains": [
        "hacky.com"
      ],
      "DistinguishedName": "CN=Domain Block List,CN=Hosted Content Filter,CN=Transport Settings,CN=Configuration,CN=example.com,CN=ConfigurationUnits,DC=NAMPR12A004,DC=PROD,DC=OUTLOOK,DC=COM",
      "Guid": "fe557a1b-e0fa-4c13-8674-c4da30a8e884",
      "Name": "Domain Block List"
    }
  ]
}
```

#### Get Tenant Allow/Block List Items

This action is used to retrieve entries from the Tenant Allow/Block List filtered by list type and action

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|action_type|string|None|False|Filter by allow or block entries. Leave empty to return both|["Allow", "Block", ""]|Block|None|None|
|list_type|string|None|True|The type of entries to retrieve|["Sender", "Url", "FileHash", "IP"]|Sender|None|None|
  
Example input:

```
{
  "action_type": "Block",
  "list_type": "Sender"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|entries|[]tenant_allow_block_list_entry|True|List of Tenant Allow/Block List entries|[{"Identity": "RgAAAAAI8gSyOVN1GYaKkFe7hRJnBwA87CsZ-sample", "Value": "evil@example.com", "Action": "Block", "ListType": "Sender", "ExpirationDate": "2026-08-14T00:00:00Z", "Notes": "Phishing sender", "LastModifiedDateTime": "2026-07-14T12:00:00Z", "CreatedDateTime": "2026-07-14T12:00:00Z"}]|
  
Example output:

```
{
  "entries": [
    {
      "Action": "Block",
      "CreatedDateTime": "2026-07-14T12:00:00Z",
      "ExpirationDate": "2026-08-14T00:00:00Z",
      "Identity": "RgAAAAAI8gSyOVN1GYaKkFe7hRJnBwA87CsZ-sample",
      "LastModifiedDateTime": "2026-07-14T12:00:00Z",
      "ListType": "Sender",
      "Notes": "Phishing sender",
      "Value": "evil@example.com"
    }
  ]
}
```

#### Email Compliance Purge

This action is used to purge a provided email

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|compliance_search_name|string|None|True|Name of compliance search|None|InsightConnect Compliance Search|None|None|
|query_timeout|integer|60|False|Query timeout in minutes|None|60|None|None|
  
Example input:

```
{
  "compliance_search_name": "InsightConnect Compliance Search",
  "query_timeout": 60
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|success|boolean|True|Success|True|
  
Example output:

```
{
  "success": true
}
```

#### Email Compliance Search and Purge

This action is used to search and purge a provided email

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|compliance_search_name|string|None|True|Name of compliance search|None|InsightConnect Compliance Search|None|None|
|content_match_query|string|None|True|This parameter uses a text search string or a query that's formatted by using the Keyword Query Language (KQL). For more information about KQL, see Keyword Query Language syntax reference (https://go.microsoft.com/fwlink/p/?linkid=269603)|None|from:example AND subject:"Click Me!"|None|None|
|delete_items|boolean|False|False|The script only executes the delete action if this parameter is true|None|True|None|None|
|query_timeout|integer|60|False|Query timeout in minutes|None|60|None|None|
  
Example input:

```
{
  "compliance_search_name": "InsightConnect Compliance Search",
  "content_match_query": "from:example AND subject:\"Click Me!\"",
  "delete_items": false,
  "query_timeout": 60
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|success|boolean|True|Success|True|
  
Example output:

```
{
  "success": true
}
```

#### Message Trace

This action is used to run a message trace

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|Sender_address|string|None|True|Sender e-mail address|None|user@example.com|None|None|
|end_date|string|None|True|End date in format MM/DD/YYYY|None|09/27/2019|None|None|
|start_date|string|None|True|Start date in format MM/DD/YYYY|None|09/27/2019|None|None|
  
Example input:

```
{
  "Sender_address": "user@example.com",
  "end_date": "09/27/2019",
  "start_date": "09/27/2019"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|message_traces|[]message_trace|True|Message Trace results|[ { "PSComputerName": "outlook.office365.com", "RunspaceId": "eb0ea814-0c3d-45eb-a189-f41118e8582d", "PSShowComputerName": false, "Organization": "things.com", "MessageId": "<***********************.namprd12.prod.outlook.com>", "Received": "2019-09-24T14:18:57.4237718", "SenderAddress": "user@example.com", "RecipientAddress": "user@example.com", "Subject": "Android Update 5.2.1", "Status": "Delivered", "ToIP": null, "FromIP": "216.93.244.203", "Size": 15846, "MessageTraceId": "d7b67cd8-a69c-46e5-8816-08d740fa2349", "StartDate": "2019-09-20T00:00:00", "EndDate": "2019-09-25T00:00:00", "Index": 0 } ]|
  
Example output:

```
{
  "message_traces": [
    {
      "EndDate": "2019-09-25T00:00:00",
      "FromIP": "216.93.244.203",
      "Index": 0,
      "MessageId": "<***********************.namprd12.prod.outlook.com>",
      "MessageTraceId": "d7b67cd8-a69c-46e5-8816-08d740fa2349",
      "Organization": "things.com",
      "PSComputerName": "outlook.office365.com",
      "PSShowComputerName": false,
      "Received": "2019-09-24T14:18:57.4237718",
      "RecipientAddress": "user@example.com",
      "RunspaceId": "eb0ea814-0c3d-45eb-a189-f41118e8582d",
      "SenderAddress": "user@example.com",
      "Size": 15846,
      "StartDate": "2019-09-20T00:00:00",
      "Status": "Delivered",
      "Subject": "Android Update 5.2.1",
      "ToIP": null
    }
  ]
}
```

#### Remove Tenant Allow/Block List Entry

This action is used to remove entries from the Tenant Allow/Block List by specifying the list type and values to remove

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|entries|[]string|None|True|Values to remove from the list. Must match existing entry values exactly|None|["evil@example.com"]|evil@example.com|None|
|list_type|string|None|True|The type of entries to remove|["Sender", "Url", "FileHash", "IP"]|Sender|None|None|
  
Example input:

```
{
  "entries": [
    "evil@example.com"
  ],
  "list_type": "Sender"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|success|boolean|True|Whether the entries were removed successfully|True|
  
Example output:

```
{
  "success": true
}
```

#### Update List of Blocked Domains

This action is used to add or remove domains from blocked domain list

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|domains|[]string|None|True|Domains which will be blocked|None|["example.com", "example2.com"]|None|None|
|identity|string|None|True|The Identity parameter specifies the spam filter policy that you want to view. Could be Name/Distinguished name (DN)/GUID|None|Domain Block List|None|None|
|operation|string|None|True|Operation which will be apply on list of blocked domains|["Add", "Remove"]|Add|None|None|
  
Example input:

```
{
  "domains": [
    "example.com",
    "example2.com"
  ],
  "identity": "Domain Block List",
  "operation": "Add"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|success|boolean|True|Success of operation|True|
  
Example output:

```
{
  "success": true
}
```
### Triggers
  
*This plugin does not contain any triggers.*
### Tasks
  
*This plugin does not contain any tasks.*

### Custom Types
  
**message_trace**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Message ID|string|None|True|ID of found email|None|
|Organization|string|None|True|Organization that message trace was run on|None|
|Received Date|string|None|True|Date email was received|None|
|Recipient Address|string|None|True|Recipient address|None|
|Sender Address|string|None|True|Sender address|None|
|Subject|string|None|True|Subject|None|
  
**spam_policy**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Blocked Sender Domains|[]string|None|False|List of blocked sender domains|None|
|Distinguished Name|string|None|False|Distinguished name (DN)|None|
|GUID|string|None|False|GUID attribute|None|
|Name|string|None|False|Name of policy|None|
  
**tenant_allow_block_list_entry**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Action|string|None|False|Whether this is an Allow or Block entry|None|
|Created Date Time|string|None|False|When the entry was created|None|
|Expiration Date|string|None|False|The expiration date of the entry in UTC|None|
|Identity|string|None|False|Unique identifier of the entry|None|
|Last Modified Date Time|string|None|False|When the entry was last modified|None|
|List Type|string|None|False|The type of entry (Sender, URL, FileHash, or IP)|None|
|Notes|string|None|False|Notes associated with the entry|None|
|Value|string|None|False|The blocked or allowed value (URL, sender, file hash, or IP)|None|


## Troubleshooting

* Queries are expected to be wrapped in quotes e.g. subject:"a subject"
* If the 8192 character (per rule) limit is reached when adding additional conditions/emails to an existing rule, conditions/emails within that rule will need to be deleted to allow for the addition of new conditions/emails.
* If the 20480 bytes (overall limit for all rules combined) is reached when making a new rule, existing rules can be deleted to make space, otherwise deleting conditions/emails within existing rules will allow for the addition of a new rule'

# Version History

* 4.1.0 - Add Tenant Allow/Block List actions: Get Items, Create Entry, Remove Entry | Updated SDK to 6.6.0
* 4.0.8 - Fixed `mass_purge` action timing out due to backslash escape characters being injected into `content_match_query` | Improved error handling | Updated SDK to the latest version (6.5.0)
* 4.0.7 - Updated `Exchange Online` module version to `3.9.2` | Updated SDK to the latest version (6.4.2)
* 4.0.6 - Script update to address Block Sender Transport Rules issues
* 4.0.5 - Updated 'block_sender_transport_rule' action to handle additional domain or email to be blocked | Updated SDK to the latest version (6.3.10)
* 4.0.4 - Adding Powershell package back in Dockerfile
* 4.0.3 - Updating documentation regarding 'block_sender_transport_rule' action | SDK Bump to 6.2.0 | Bumping requirements.txt
* 4.0.2 - Updated the SDK to latest version | Updated the `Exchange Online` module version to `3.4.0` | `Email Compliance Search`: Invalid characters are being stripped from `Compliance Search Name`
* 4.0.1 - Updated the SDK version | Updated the `Exchange Online` module version
* 4.0.0 - Remove Basic Authentication connection. Added Modern Authentication(OAuth) for ExchangeOnline Powershell and Security & Compliance PowerShell. Connection Input Office365 URL is no longer required. This change is due to the fact Basic Authentication for Exchange Online has now been deprecated. For further information on this, please view the resources listed at the bottom of this help document.
* 3.0.3 - Fixing the release issues related to 3.0.2
* 3.0.2 - Fix the bug related to JSON marshalling
* 3.0.1 - Search through multiple mailboxes in Email Compilance Search
* 3.0.0 - Create new actions Update List of Blocked Domains and Get List of Blocked Domains | Create one class to communicate with Microsoft Outlook | Update SDK to version 4 | Fix Email Compliance Purge action bug with bytes in output
* 2.3.5 - Add logger in `Transport-Rules.ps1` | Change silent 'stop' to 'SilentlyContinue'
* 2.3.4 - Fixed bugs impacting searches where the name contained a space, impacting the Block Sender Transport Rule action, and empty message traces errors.
* 2.3.3 - Updated all actions to automatically monitor and reconnect when needed. Fixed several other minor bugs.
* 2.3.2 - Added try/catch handling for remote powershell commands (all actions)
* 2.3.1 - Update error handling for cleaner and clearer logs on errors
* 2.3.0 - Add Exchange Location to Email Compliance Search action | Update to make Email Compliance Search action overwrite existing searches instead of just rerunning them
* 2.2.7 - Fix issue where connection test could use the wrong URI to authenticate which could cause false test results
* 2.2.6 - Update to make error logging more visible in the Email Compliance Search action
* 2.2.5 - Fix issue where creating a new compliance search could fail by prompting the user for confirmation on continue
* 2.2.4 - Add example inputs in all actions | Move connection to new `ps` script | Fix method name in Message Trace action | Defined instance attributes inside `_init_` in connection file | Regenerate help.md | Change user in Dockerfile to `nobody`
* 2.2.3 - Update to add logging to warn of dollar sign in password Microsoft bug
* 2.2.2 - Updated out of date Powershell module in Email Security Compliance Search
* 2.2.1 - New spec and help.md format for the Extension Library
* 2.2.0 - New action Message Trace
* 2.1.0 - Add user email address array to Search action
* 2.0.0 - New actions Mass Search, Purge and combined Search and Purge
* 1.0.1 - Fix issue where plugin would fail when creating transport rule on first run
* 1.0.0 - Initial plugin

# Links

* [Connect to Security & Compliance PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell?view=exchange-ps)

## References

* [Microsoft Office365 ](https://www.office.com/)
* [Transport Rule Limits](https://docs.microsoft.com/en-us/office365/servicedescriptions/exchange-online-service-description/exchange-online-limits#journal-transport-and-inbox-rule-limits)
* [New-TransportRule](https://docs.microsoft.com/en-us/powershell/module/exchange/policy-and-compliance/new-transportrule?view=exchange-ps)
* [Set-TransportRule](https://docs.microsoft.com/en-us/powershell/module/exchange/policy-and-compliance/set-transportrule?view=exchange-ps)
* [Connect to Security & Compliance PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell?view=exchange-ps)