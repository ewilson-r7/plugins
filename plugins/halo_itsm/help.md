# Description

Halo ITSM is a cloud-based IT Service Management platform that provides ticket management, asset tracking, and service desk capabilities

# Key Features

* Create, update, delete, and get tickets
* List tickets with filtering support
* Add actions (notes/comments) to tickets
* Manage ticket assignments and status changes

# Requirements

* Halo ITSM API Client ID and Client Secret
* Base URL of your Halo ITSM instance
* API application configured with Client Credentials grant type in Halo ITSM

# Supported Product Versions

* 2025-07-10

# Documentation

## Setup

The connection configuration accepts the following parameters:  

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|base_url|string|None|True|Base URL of your Halo ITSM instance (e.g. https://your-instance.haloitsm.com)|None|https://example.haloitsm.com|None|None|
|client_id|string|None|True|OAuth Client ID for the Halo ITSM API application|None|a1b2c3d4-e5f6-7890-abcd-ef1234567890|None|None|
|client_secret|credential_secret_key|None|True|OAuth Client Secret for the Halo ITSM API application|None|{"secretKey": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"}|None|None|
|tenant|string|None|False|Tenant name for multi-tenant Halo ITSM instances (optional, leave blank if not applicable)|None|my-tenant|None|None|

Example input:

```
{
  "base_url": "https://example.haloitsm.com",
  "client_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "client_secret": {
    "secretKey": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "tenant": "my-tenant"
}
```

## Technical Details

### Actions


#### Add Action to Ticket

This action is used to add an action (note, comment, or update) to an existing ticket

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|hiddenfromuser|boolean|False|False|Whether this note should be hidden from the end user|None|False|None|None|
|note|string|None|True|Content of the action note in plain text or HTML|None|Investigated the issue and found root cause|None|None|
|outcome|string|None|False|Outcome of the action|None|Ongoing|None|None|
|ticket_id|integer|None|True|ID of the ticket to add the action to|None|1234|None|None|
  
Example input:

```
{
  "hiddenfromuser": false,
  "note": "Investigated the issue and found root cause",
  "outcome": "Ongoing",
  "ticket_id": 1234
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|action|ticket_action|True|The newly created action|{"id":501,"ticket_id":1234,"who":"John Smith","note":"Investigated the issue and found root cause","hiddenfromuser":false,"outcome":"Ongoing","actiondate":"2025-07-10T10:30:00Z"}|
  
Example output:

```
{
  "action": {
    "actiondate": "2025-07-10T10:30:00Z",
    "hiddenfromuser": false,
    "id": 501,
    "note": "Investigated the issue and found root cause",
    "outcome": "Ongoing",
    "ticket_id": 1234,
    "who": "John Smith"
  }
}
```

#### Attach File to Ticket

This action is used to attach a file to an existing ticket via an action note

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|content|bytes|None|True|Base64-encoded content of the file to attach|None|VGhpcyBpcyBhIHRlc3QgZmlsZQ==|None|None|
|filename|string|None|True|Name of the file to attach (e.g. screenshot.png)|None|error_log.txt|None|None|
|hiddenfromuser|boolean|False|False|Whether the attachment action should be hidden from the end user|None|False|None|None|
|note|string|None|False|Optional note to include with the attachment|None|Attaching error log for reference|None|None|
|ticket_id|integer|None|True|ID of the ticket to attach the file to|None|1234|None|None|
  
Example input:

```
{
  "content": "VGhpcyBpcyBhIHRlc3QgZmlsZQ==",
  "filename": "error_log.txt",
  "hiddenfromuser": false,
  "note": "Attaching error log for reference",
  "ticket_id": 1234
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|action|ticket_action|True|The action created with the attachment|{"id":502,"ticket_id":1234,"who":"John Smith","note":"Attaching error log for reference","hiddenfromuser":false,"outcome":null,"actiondate":"2025-07-10T11:00:00Z"}|
  
Example output:

```
{
  "action": {
    "actiondate": "2025-07-10T11:00:00Z",
    "hiddenfromuser": false,
    "id": 502,
    "note": "Attaching error log for reference",
    "outcome": null,
    "ticket_id": 1234,
    "who": "John Smith"
  }
}
```

#### Create Ticket

This action is used to create a new ticket in Halo ITSM

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|agent_id|integer|None|False|ID of the agent to assign the ticket to|None|15|None|None|
|category_1|string|None|False|Primary category of the ticket|None|Hardware|None|None|
|category_2|string|None|False|Subcategory of the ticket|None|Laptop|None|None|
|client_id|integer|None|False|ID of the client associated with the ticket|None|5|None|None|
|details|string|None|False|Full details of the ticket in plain text or HTML|None|The production server has been unresponsive since 10:00 AM|None|None|
|impact|string|None|False|Impact level of the ticket|None|Medium|None|None|
|priority_id|integer|None|False|ID of the ticket priority|None|3|None|None|
|site_id|integer|None|False|ID of the site to associate with the ticket|None|2|None|None|
|status_id|integer|None|False|ID of the initial status for the ticket|None|1|None|None|
|summary|string|None|True|Summary of the ticket|None|Server is unresponsive|None|None|
|tickettype_id|integer|None|True|ID of the ticket type (e.g. 1 for Incident, 2 for Service Request)|None|1|None|None|
|urgency|string|None|False|Urgency level of the ticket|None|High|None|None|
|user_id|integer|None|False|ID of the user raising the ticket|None|10|None|None|
  
Example input:

```
{
  "agent_id": 15,
  "category_1": "Hardware",
  "category_2": "Laptop",
  "client_id": 5,
  "details": "The production server has been unresponsive since 10:00 AM",
  "impact": "Medium",
  "priority_id": 3,
  "site_id": 2,
  "status_id": 1,
  "summary": "Server is unresponsive",
  "tickettype_id": 1,
  "urgency": "High",
  "user_id": 10
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|ticket|ticket|True|The newly created ticket|{"id":101,"summary":"Server is unresponsive","details":"The production server has been unresponsive since 10:00 AM","status_id":1,"priority_id":3,"tickettype_id":1,"category_1":"Hardware","category_2":"Server","impact":"Medium","urgency":"High","user_id":10,"user_name":"Jane Doe","agent_id":15,"agent_name":"John Smith","team":"IT Support","dateoccurred":"2025-07-10T10:00:00Z","datecreated":"2025-07-10T10:05:00Z","lastupdate":"2025-07-10T10:05:00Z","closeddate":null,"client_id":5,"client_name":"ACME Corp","site_id":2,"sla_id":1}|
  
Example output:

```
{
  "ticket": {
    "agent_id": 15,
    "agent_name": "John Smith",
    "category_1": "Hardware",
    "category_2": "Server",
    "client_id": 5,
    "client_name": "ACME Corp",
    "closeddate": null,
    "datecreated": "2025-07-10T10:05:00Z",
    "dateoccurred": "2025-07-10T10:00:00Z",
    "details": "The production server has been unresponsive since 10:00 AM",
    "id": 101,
    "impact": "Medium",
    "lastupdate": "2025-07-10T10:05:00Z",
    "priority_id": 3,
    "site_id": 2,
    "sla_id": 1,
    "status_id": 1,
    "summary": "Server is unresponsive",
    "team": "IT Support",
    "tickettype_id": 1,
    "urgency": "High",
    "user_id": 10,
    "user_name": "Jane Doe"
  }
}
```

#### Delete Ticket

This action is used to delete a ticket from Halo ITSM

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|ticket_id|integer|None|True|ID of the ticket to delete|None|1234|None|None|
  
Example input:

```
{
  "ticket_id": 1234
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|success|boolean|True|Whether the ticket was successfully deleted|True|
  
Example output:

```
{
  "success": true
}
```

#### Get Ticket

This action is used to get details of a specific ticket by ID

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|ticket_id|integer|None|True|ID of the ticket to retrieve|None|1234|None|None|
  
Example input:

```
{
  "ticket_id": 1234
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|ticket|ticket|True|The ticket details|{"id":1234,"summary":"Email not working","details":"User reports email client is not connecting to server","status_id":2,"priority_id":2,"tickettype_id":1,"category_1":"Software","category_2":"Email","impact":"High","urgency":"High","user_id":20,"user_name":"Jane Doe","agent_id":15,"agent_name":"John Smith","team":"IT Support","dateoccurred":"2025-07-09T14:00:00Z","datecreated":"2025-07-09T14:05:00Z","lastupdate":"2025-07-10T08:30:00Z","closeddate":null,"client_id":5,"client_name":"ACME Corp","site_id":1,"sla_id":2}|
  
Example output:

```
{
  "ticket": {
    "agent_id": 15,
    "agent_name": "John Smith",
    "category_1": "Software",
    "category_2": "Email",
    "client_id": 5,
    "client_name": "ACME Corp",
    "closeddate": null,
    "datecreated": "2025-07-09T14:05:00Z",
    "dateoccurred": "2025-07-09T14:00:00Z",
    "details": "User reports email client is not connecting to server",
    "id": 1234,
    "impact": "High",
    "lastupdate": "2025-07-10T08:30:00Z",
    "priority_id": 2,
    "site_id": 1,
    "sla_id": 2,
    "status_id": 2,
    "summary": "Email not working",
    "team": "IT Support",
    "tickettype_id": 1,
    "urgency": "High",
    "user_id": 20,
    "user_name": "Jane Doe"
  }
}
```

#### List Tickets

This action is used to list tickets from Halo ITSM with optional filtering

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|agent_id|integer|None|False|Filter tickets by assigned agent ID|None|15|None|None|
|client_id|integer|None|False|Filter tickets by client ID|None|5|None|None|
|count|integer|50|False|Maximum number of tickets to return|None|50|None|None|
|search|string|None|False|Search string to filter tickets|None|server down|Enter search term|None|
|status_id|integer|None|False|Filter tickets by status ID|None|1|None|None|
|tickettype_id|integer|None|False|Filter tickets by ticket type ID|None|1|None|None|
  
Example input:

```
{
  "agent_id": 15,
  "client_id": 5,
  "count": 50,
  "search": "server down",
  "status_id": 1,
  "tickettype_id": 1
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|tickets|[]ticket|True|List of tickets matching the filter criteria|[{"id":1234,"summary":"Email not working","status_id":2,"priority_id":2,"tickettype_id":1,"category_1":"Software","agent_id":15,"agent_name":"John Smith","client_name":"ACME Corp"},{"id":1235,"summary":"Printer jam on 3rd floor","status_id":1,"priority_id":4,"tickettype_id":1,"category_1":"Hardware","agent_id":null,"agent_name":null,"client_name":"ACME Corp"}]|
  
Example output:

```
{
  "tickets": [
    {
      "agent_id": 15,
      "agent_name": "John Smith",
      "category_1": "Software",
      "client_name": "ACME Corp",
      "id": 1234,
      "priority_id": 2,
      "status_id": 2,
      "summary": "Email not working",
      "tickettype_id": 1
    },
    {
      "agent_id": null,
      "agent_name": null,
      "category_1": "Hardware",
      "client_name": "ACME Corp",
      "id": 1235,
      "priority_id": 4,
      "status_id": 1,
      "summary": "Printer jam on 3rd floor",
      "tickettype_id": 1
    }
  ]
}
```

#### Update Ticket

This action is used to update an existing ticket in Halo ITSM

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|agent_id|integer|None|False|Updated agent ID to assign the ticket to|None|15|None|None|
|category_1|string|None|False|Updated primary category|None|Software|None|None|
|category_2|string|None|False|Updated subcategory|None|Operating System|None|None|
|details|string|None|False|Updated details of the ticket|None|Updated details text|None|None|
|impact|string|None|False|Updated impact level|None|High|None|None|
|priority_id|integer|None|False|Updated priority ID for the ticket|None|1|None|None|
|status_id|integer|None|False|Updated status ID for the ticket|None|2|None|None|
|summary|string|None|False|Updated summary of the ticket|None|Updated summary|None|None|
|ticket_id|integer|None|True|ID of the ticket to update|None|1234|None|None|
|urgency|string|None|False|Updated urgency level|None|Critical|None|None|
  
Example input:

```
{
  "agent_id": 15,
  "category_1": "Software",
  "category_2": "Operating System",
  "details": "Updated details text",
  "impact": "High",
  "priority_id": 1,
  "status_id": 2,
  "summary": "Updated summary",
  "ticket_id": 1234,
  "urgency": "Critical"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|ticket|ticket|True|The updated ticket|{"id":1234,"summary":"Email not working - UPDATED","details":"User reports email client is not connecting to server. Investigating.","status_id":3,"priority_id":1,"tickettype_id":1,"category_1":"Software","category_2":"Email","impact":"High","urgency":"Critical","user_id":20,"user_name":"Jane Doe","agent_id":15,"agent_name":"John Smith","team":"IT Support","dateoccurred":"2025-07-09T14:00:00Z","datecreated":"2025-07-09T14:05:00Z","lastupdate":"2025-07-10T09:00:00Z","closeddate":null,"client_id":5,"client_name":"ACME Corp","site_id":1,"sla_id":2}|
  
Example output:

```
{
  "ticket": {
    "agent_id": 15,
    "agent_name": "John Smith",
    "category_1": "Software",
    "category_2": "Email",
    "client_id": 5,
    "client_name": "ACME Corp",
    "closeddate": null,
    "datecreated": "2025-07-09T14:05:00Z",
    "dateoccurred": "2025-07-09T14:00:00Z",
    "details": "User reports email client is not connecting to server. Investigating.",
    "id": 1234,
    "impact": "High",
    "lastupdate": "2025-07-10T09:00:00Z",
    "priority_id": 1,
    "site_id": 1,
    "sla_id": 2,
    "status_id": 3,
    "summary": "Email not working - UPDATED",
    "team": "IT Support",
    "tickettype_id": 1,
    "urgency": "Critical",
    "user_id": 20,
    "user_name": "Jane Doe"
  }
}
```
### Triggers
  
*This plugin does not contain any triggers.*
### Tasks
  
*This plugin does not contain any tasks.*

### Custom Types
  
**ticket**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Agent ID|integer|None|False|ID of the agent assigned to the ticket|15|
|Agent Name|string|None|False|Name of the agent assigned to the ticket|John Smith|
|Category|string|None|False|Primary category of the ticket|Hardware|
|Subcategory|string|None|False|Subcategory of the ticket|Server|
|Client ID|integer|None|False|ID of the client associated with the ticket|5|
|Client Name|string|None|False|Name of the client associated with the ticket|ACME Corp|
|Closed Date|string|None|False|Timestamp when the ticket was closed|2025-07-11 09:00:00+00:00|
|Date Created|string|None|False|Timestamp when the ticket was created|2025-07-10 10:05:00+00:00|
|Date Occurred|string|None|False|Date when the ticket was raised|2025-07-10 10:00:00+00:00|
|Details|string|None|False|Details of the ticket|The production server has been unresponsive since 10:00 AM|
|ID|integer|None|False|Unique ID of the ticket|1234|
|Impact|string|None|False|Impact level of the ticket|Medium|
|Last Update|string|None|False|Timestamp of the last update on the ticket|2025-07-10 11:30:00+00:00|
|Priority ID|integer|None|False|ID of the ticket priority|3|
|Site ID|integer|None|False|ID of the site associated with the ticket|2|
|SLA ID|integer|None|False|ID of the SLA applied to the ticket|1|
|Status ID|integer|None|False|ID of the ticket status|1|
|Summary|string|None|False|Summary of the ticket|Server is unresponsive|
|Team|string|None|False|Team assigned to the ticket|IT Support|
|Ticket Type ID|integer|None|False|ID of the ticket type|1|
|Urgency|string|None|False|Urgency level of the ticket|High|
|User ID|integer|None|False|ID of the user who raised the ticket|10|
|User Name|string|None|False|Name of the user who raised the ticket|Jane Doe|
  
**ticket_action**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Action Date|string|None|False|Timestamp of the action|2025-07-10 10:30:00+00:00|
|Hidden from User|boolean|None|False|Whether the action is hidden from the end user|False|
|ID|integer|None|False|Unique ID of the action|501|
|Note|string|None|False|Content of the action note|Investigated the issue and found root cause|
|Outcome|string|None|False|Outcome of the action|Ongoing|
|Ticket ID|integer|None|False|ID of the ticket this action belongs to|1234|
|Who|string|None|False|Name of the person who performed the action|John Smith|


## Troubleshooting
  
*This plugin does not contain a troubleshooting.*

# Version History

* 1.0.0 - Initial plugin release with Create, Get, Update, Delete, List Tickets, Add Action, and Attach File actions

# Links

* [Halo ITSM](https://haloitsm.com)

## References

* [Halo ITSM API Guide](https://haloitsm.com/guides/article/?kbid=929)