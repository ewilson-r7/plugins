# Description

Manage endpoint collections, hunts, and artifact deployments using the Rapid7 Velociraptor API

# Key Features

* Search and retrieve endpoint client information
* Launch targeted artifact collections on specific endpoints
* Create and monitor fleet-wide threat hunts
* Retrieve collection and hunt results for investigation
* Manage client labels for incident tracking
* Browse available Velociraptor artifacts

# Requirements

* Rapid7 Velociraptor API key
* Organization ID from the Velociraptor platform

# Supported Product Versions

* Velociraptor API v1 2025-07-22

# Documentation

## Setup

The connection configuration accepts the following parameters:  

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|api_key|credential_secret_key|None|True|Rapid7 Platform API key|None|{"secretKey": "abc123-def456-ghi789"}|None|None|
|org_id|string|None|True|Velociraptor organization ID|None|686a33ec-88b9-4f84-bddf-2a1fb0fecb85|686a33ec-88b9-4f84-bddf-2a1fb0fecb85|None|
|region|string|None|True|Rapid7 platform region|["us", "us2", "us3", "eu", "au", "ca", "ap", "jp"]|us|None|None|

Example input:

```
{
  "api_key": {
    "secretKey": "abc123-def456-ghi789"
  },
  "org_id": "686a33ec-88b9-4f84-bddf-2a1fb0fecb85",
  "region": "us"
}
```

## Technical Details

### Actions


#### Add Label

This action is used to add a label to a client for tracking during incident response

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|client_id|string|None|True|The unique identifier of the client|None|C.1234567890abcdef|None|None|
|label|string|None|True|The label to add to the client|None|compromised|compromised|None|
  
Example input:

```
{
  "client_id": "C.1234567890abcdef",
  "label": "compromised"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|label_response|label_response|False|Confirmation of the label addition|{"client_id": "C.1234567890abcdef", "label": "compromised"}|
  
Example output:

```
{
  "label_response": {
    "client_id": "C.1234567890abcdef",
    "label": "compromised"
  }
}
```

#### Create Flow

This action is used to launch an artifact collection on a specific client endpoint

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|artifacts|[]string|None|True|List of artifact names to collect|None|["Windows.System.ProcessList", "Windows.Network.Netstat"]|None|None|
|client_id|string|None|True|The unique identifier of the client to collect from|None|C.1234567890abcdef|None|None|
|max_rows|integer|None|False|Maximum number of rows to collect per artifact|None|10000|None|None|
|timeout|integer|600|False|Collection timeout in seconds|None|600|None|None|
|urgent|boolean|False|False|Whether to prioritize this collection|None|False|None|None|
  
Example input:

```
{
  "artifacts": [
    "Windows.System.ProcessList",
    "Windows.Network.Netstat"
  ],
  "client_id": "C.1234567890abcdef",
  "max_rows": 10000,
  "timeout": 600,
  "urgent": false
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|flow_id|string|False|The unique identifier of the created flow|F.C8FJK2L3M|
  
Example output:

```
{
  "flow_id": "F.C8FJK2L3M"
}
```

#### Create Hunt

This action is used to create a new fleet-wide threat hunt to collect artifacts across multiple endpoints

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|artifacts|[]string|None|True|List of artifact names to collect in this hunt|None|["Windows.System.PowerShell.ScriptBlockLog"]|None|None|
|client_limit|integer|None|False|Maximum number of clients to schedule the hunt on|None|500|None|None|
|exclude_labels|[]string|None|False|Exclude clients with these labels|None|["decommissioned"]|None|None|
|expires|integer|None|False|Hunt expiration time as a Unix timestamp|None|1735689600|None|None|
|hunt_description|string|None|True|A description of the hunt purpose|None|Hunt for suspicious PowerShell activity|Hunt for suspicious PowerShell activity|None|
|include_labels|[]string|None|False|Only target clients with these labels|None|["under_investigation"]|None|None|
|os_condition|string|ALL|False|Target operating system for the hunt|["ALL", "WINDOWS", "LINUX", "OSX"]|WINDOWS|None|None|
  
Example input:

```
{
  "artifacts": [
    "Windows.System.PowerShell.ScriptBlockLog"
  ],
  "client_limit": 500,
  "exclude_labels": [
    "decommissioned"
  ],
  "expires": 1735689600,
  "hunt_description": "Hunt for suspicious PowerShell activity",
  "include_labels": [
    "under_investigation"
  ],
  "os_condition": "ALL"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|hunt_id|string|False|The unique identifier of the created hunt|H.abcdef1234|
  
Example output:

```
{
  "hunt_id": "H.abcdef1234"
}
```

#### Get Client

This action is used to retrieve details for a specific Velociraptor client endpoint

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|client_id|string|None|True|The unique identifier of the client|None|C.1234567890abcdef|None|None|
  
Example input:

```
{
  "client_id": "C.1234567890abcdef"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|client|client|False|Client endpoint details|{"client_id": "C.1234567890abcdef", "hostname": "WORKSTATION-01", "system": "windows"}|
  
Example output:

```
{
  "client": {
    "client_id": "C.1234567890abcdef",
    "hostname": "WORKSTATION-01",
    "system": "windows"
  }
}
```

#### Get Client Labels

This action is used to list all labels assigned to a specific client

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|client_id|string|None|True|The unique identifier of the client|None|C.1234567890abcdef|None|None|
  
Example input:

```
{
  "client_id": "C.1234567890abcdef"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|labels|[]string|False|List of labels assigned to the client|["compromised", "under_investigation"]|
  
Example output:

```
{
  "labels": [
    "compromised",
    "under_investigation"
  ]
}
```

#### Get Flow

This action is used to retrieve the status and details of a specific flow collection

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|client_id|string|None|True|The unique identifier of the client|None|C.1234567890abcdef|None|None|
|flow_id|string|None|True|The unique identifier of the flow|None|F.C8FJK2L3M|None|None|
  
Example input:

```
{
  "client_id": "C.1234567890abcdef",
  "flow_id": "F.C8FJK2L3M"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|flow|flow|False|Flow collection details and status|{"client_id": "C.1234567890abcdef", "session_id": "F.C8FJK2L3M", "state": "FINISHED"}|
  
Example output:

```
{
  "flow": {
    "client_id": "C.1234567890abcdef",
    "session_id": "F.C8FJK2L3M",
    "state": "FINISHED"
  }
}
```

#### Get Flow Results

This action is used to retrieve the results of a completed flow collection for a specific artifact

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|artifact|string|None|True|The artifact name to retrieve results for|None|Windows.System.ProcessList|Windows.System.ProcessList|None|
|client_id|string|None|True|The unique identifier of the client|None|C.1234567890abcdef|None|None|
|flow_id|string|None|True|The unique identifier of the flow|None|F.C8FJK2L3M|None|None|
  
Example input:

```
{
  "artifact": "Windows.System.ProcessList",
  "client_id": "C.1234567890abcdef",
  "flow_id": "F.C8FJK2L3M"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|count|integer|False|Number of result rows returned|25|
|results|[]object|False|Collection result data rows|[{"Name": "svchost.exe", "Pid": 1234}]|
  
Example output:

```
{
  "count": 25,
  "results": [
    {
      "Name": "svchost.exe",
      "Pid": 1234
    }
  ]
}
```

#### Get Hunt

This action is used to retrieve details and status of a specific threat hunt

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|hunt_id|string|None|True|The unique identifier of the hunt|None|H.abcdef1234|None|None|
  
Example input:

```
{
  "hunt_id": "H.abcdef1234"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|hunt_details|hunt_details|False|Hunt configuration, state, and statistics|{"hunt_id": "H.abcdef1234", "state": "RUNNING"}|
  
Example output:

```
{
  "hunt_details": {
    "hunt_id": "H.abcdef1234",
    "state": "RUNNING"
  }
}
```

#### Get Hunt Results

This action is used to retrieve results collected by a specific threat hunt

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|hunt_id|string|None|True|The unique identifier of the hunt|None|H.abcdef1234|None|None|
|limit|integer|100|False|Maximum number of results to return|None|100|None|None|
  
Example input:

```
{
  "hunt_id": "H.abcdef1234",
  "limit": 100
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|count|integer|False|Number of result sets returned|10|
|results|[]hunt_result|False|Hunt result sets from targeted clients|[{"client_id": "C.1234567890abcdef", "artifact": "Windows.System.ProcessList"}]|
  
Example output:

```
{
  "count": 10,
  "results": [
    {
      "artifact": "Windows.System.ProcessList",
      "client_id": "C.1234567890abcdef"
    }
  ]
}
```

#### List Artifacts

This action is used to browse available Velociraptor artifact definitions for use in collections and hunts

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|artifact_type|string|ALL|False|Filter by artifact type|["ALL", "CLIENT", "CLIENT_EVENT", "SERVER", "SERVER_EVENT", "NOTEBOOK"]|CLIENT|None|None|
|include_built_in|boolean|True|False|Include built-in artifacts in results|None|True|None|None|
|include_custom|boolean|True|False|Include custom artifacts in results|None|True|None|None|
|os|string|ALL|False|Filter by target operating system|["ALL", "LINUX", "WINDOWS", "DARWIN"]|WINDOWS|None|None|
  
Example input:

```
{
  "artifact_type": "ALL",
  "include_built_in": true,
  "include_custom": true,
  "os": "ALL"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|artifacts|[]artifact_listing|False|List of available artifact definitions|[{"name": "Windows.System.ProcessList", "type": "CLIENT", "built_in": true}]|
|count|integer|False|Number of artifacts returned|150|
  
Example output:

```
{
  "artifacts": [
    {
      "built_in": true,
      "name": "Windows.System.ProcessList",
      "type": "CLIENT"
    }
  ],
  "count": 150
}
```

#### List Clients

This action is used to search and list Velociraptor client endpoints with optional filters

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|hostname|string|None|False|Filter by hostname substring|None|WORKSTATION-01|WORKSTATION-01|None|
|label|string|None|False|Filter by client label|None|compromised|compromised|None|
|limit|integer|100|False|Maximum number of results to return|None|100|None|None|
|os|string|None|False|Filter by operating system|None|windows|windows|None|
|status|string|ALL|False|Filter by client online status|["ALL", "ONLINE", "OFFLINE"]|ALL|None|None|
  
Example input:

```
{
  "hostname": "WORKSTATION-01",
  "label": "compromised",
  "limit": 100,
  "os": "windows",
  "status": "ALL"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|clients|[]client|False|List of client endpoints matching the search criteria|[{"client_id": "C.1234567890abcdef", "hostname": "WORKSTATION-01"}]|
|count|integer|False|Number of clients returned|1|
  
Example output:

```
{
  "clients": [
    {
      "client_id": "C.1234567890abcdef",
      "hostname": "WORKSTATION-01"
    }
  ],
  "count": 1
}
```

#### List Flows

This action is used to list artifact collection flows for a specific client

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|client_id|string|None|True|The unique identifier of the client|None|C.1234567890abcdef|None|None|
|creator|string|None|False|Filter by flow creator username|None|admin@example.com|admin@example.com|None|
|limit|integer|50|False|Maximum number of results to return|None|50|None|None|
  
Example input:

```
{
  "client_id": "C.1234567890abcdef",
  "creator": "admin@example.com",
  "limit": 50
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|count|integer|False|Number of flows returned|1|
|flows|[]flow|False|List of flows for the client|[{"session_id": "F.C8FJK2L3M", "state": "FINISHED"}]|
  
Example output:

```
{
  "count": 1,
  "flows": [
    {
      "session_id": "F.C8FJK2L3M",
      "state": "FINISHED"
    }
  ]
}
```

#### List Hunts

This action is used to list threat hunts with optional state filter

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|limit|integer|50|False|Maximum number of results to return|None|50|None|None|
|state|string|None|False|Filter hunts by state|["UNSET", "PAUSED", "RUNNING", "STOPPED", "ARCHIVED"]|RUNNING|None|None|
  
Example input:

```
{
  "limit": 50,
  "state": "RUNNING"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|count|integer|False|Number of hunts returned|5|
|hunts|[]hunt|False|List of hunts|[{"hunt_id": "H.abcdef1234", "state": "RUNNING"}]|
  
Example output:

```
{
  "count": 5,
  "hunts": [
    {
      "hunt_id": "H.abcdef1234",
      "state": "RUNNING"
    }
  ]
}
```

#### Remove Label

This action is used to remove a label from a client

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|client_id|string|None|True|The unique identifier of the client|None|C.1234567890abcdef|None|None|
|label|string|None|True|The label to remove from the client|None|compromised|compromised|None|
  
Example input:

```
{
  "client_id": "C.1234567890abcdef",
  "label": "compromised"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|success|boolean|True|Whether the label was successfully removed|True|
  
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
  
**client**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Architecture|string|None|False|None|None|
|Client ID|string|None|False|None|None|
|Client Version|string|None|False|None|None|
|First Seen At|integer|None|False|None|None|
|Hostname|string|None|False|None|None|
|Release|string|None|False|None|None|
|System|string|None|False|None|None|
  
**hunt**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Artifacts|[]string|None|False|None|None|
|Create Time|integer|None|False|None|None|
|Creator|string|None|False|None|None|
|Expires|integer|None|False|None|None|
|Hunt Description|string|None|False|None|None|
|Hunt ID|string|None|False|None|None|
|State|string|None|False|None|None|
  
**hunt_details**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Configuration|object|None|False|None|None|
|Hunt ID|string|None|False|None|None|
|State|string|None|False|None|None|
|Statistics|object|None|False|None|None|
  
**hunt_result**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Artifact|string|None|False|None|None|
|Client ID|string|None|False|None|None|
|Flow ID|string|None|False|None|None|
|Rows|[]object|None|False|None|None|
|Total Rows|integer|None|False|None|None|
  
**flow**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Client ID|string|None|False|None|None|
|Create Time|integer|None|False|None|None|
|Outstanding Requests|integer|None|False|None|None|
|Session ID|string|None|False|None|None|
|State|string|None|False|None|None|
|Total Requests|integer|None|False|None|None|
  
**artifact_listing**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Built In|boolean|None|False|None|None|
|Description|string|None|False|None|None|
|Name|string|None|False|None|None|
|Type|string|None|False|None|None|
  
**label_response**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Client ID|string|None|False|None|None|
|Label|string|None|False|None|None|


## Troubleshooting
  
*This plugin does not contain a troubleshooting.*

# Version History

* 1.0.0 - Initial plugin release

# Links

* [Rapid7 Velociraptor](https://www.rapid7.com/products/velociraptor/)

## References

* [Velociraptor API Documentation](https://docs.velociraptor.app/)