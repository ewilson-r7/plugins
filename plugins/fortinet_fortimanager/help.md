# Description

Fortinet FortiManager is a centralized network security management platform that provides single-pane-of-glass administration for multiple FortiGate devices. This plugin enables InsightConnect SOAR workflows to manage address objects, address groups, and firewall policies through FortiManager's JSON-RPC API

# Key Features

* Create, delete, and list address objects
* Add and remove address objects from address groups
* Check if an address exists in an address group
* Retrieve firewall policies from policy packages
* Install policy packages to managed FortiGate devices

# Requirements

* Fortinet FortiManager 7.0 or later
* An API token (FortiManager 7.2.2+ recommended) or admin username and password
* Network connectivity from the InsightConnect orchestrator to FortiManager on HTTPS (port 443)

# Supported Product Versions

* 7.0.x
* 7.2.x
* 7.4.x

# Documentation

## Setup

The connection configuration accepts the following parameters:  

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|adom|string|root|True|Default Administrative Domain (ADOM) name|None|root|None|None|
|api_key|credential_secret_key|None|False|API token for Bearer authentication (required when authentication type is API Token)|None|2Fty5834tFpBdidePJnt9075MMdkUb|None|None|
|authentication_type|string|API Token|True|Authentication method to use when connecting to FortiManager|["API Token", "Session-Based"]|API Token|None|None|
|hostname|string|None|True|FortiManager hostname or IP address (e.g. fortimanager.example.com, 192.168.1.1, fortimanager.example.com:8443)|None|fortimanager.example.com|None|None|
|password|credential_secret_key|None|False|Admin password for session-based authentication (required when authentication type is Session-Based)|None|password123|None|None|
|ssl_verify|boolean|False|True|Validate TLS certificate when connecting to FortiManager|None|False|None|None|
|username|string|None|False|Admin username for session-based authentication (required when authentication type is Session-Based)|None|admin|None|None|

Example input:

```
{
  "adom": "root",
  "api_key": "2Fty5834tFpBdidePJnt9075MMdkUb",
  "authentication_type": "API Token",
  "hostname": "fortimanager.example.com",
  "password": "password123",
  "ssl_verify": false,
  "username": "admin"
}
```

## Technical Details

### Actions


#### Add Address Object to Group

This action is used to add an address object to an address group in a FortiManager ADOM

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|address_object|string|None|True|Name of the address object to add to the group|None|MaliciousHost|None|None|
|adom|string|None|False|Administrative Domain for the operation. If provided, overrides the ADOM configured in the connection|None|root|None|None|
|group|string|None|True|Name of the address group|None|InsightConnect Block List|None|None|
  
Example input:

```
{
  "address_object": "MaliciousHost",
  "adom": "root",
  "group": "InsightConnect Block List"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|address_objects|[]string|True|Updated list of address object names in the group|["MaliciousHost", "AnotherHost"]|
|success|boolean|True|Boolean value indicating the success of the operation|True|
  
Example output:

```
{
  "address_objects": [
    "MaliciousHost",
    "AnotherHost"
  ],
  "success": true
}
```

#### Check if Address in Group

This action is used to check if an address exists in an address group

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|address|string|None|True|The address to check. When Enable Search is false, this is matched against address object names. When Enable Search is true, this is matched against the stored subnet or FQDN value of each member object|None|198.51.100.100|None|None|
|adom|string|None|False|Administrative Domain for the operation. If provided, overrides the ADOM configured in the connection|None|root|None|None|
|enable_search|boolean|False|True|When enabled, the address input is compared against the stored value (subnet/FQDN) of each member object rather than matching by name|None|False|None|None|
|group|string|None|True|Name of the address group to check|None|InsightConnect Block List|None|None|
  
Example input:

```
{
  "address": "198.51.100.100",
  "adom": "root",
  "enable_search": false,
  "group": "InsightConnect Block List"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|address_objects|[]string|True|List of matching address object names found in the group|["198.51.100.100/32"]|
|found|boolean|True|Whether at least one matching address object was found in the group|True|
  
Example output:

```
{
  "address_objects": [
    "198.51.100.100/32"
  ],
  "found": true
}
```

#### Create Address Object

This action is used to create a new address object in a FortiManager ADOM

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|address|string|None|True|The address to assign to the address object. Accepts an IP address, CIDR notation, or fully qualified domain name|None|198.51.100.100|None|None|
|address_object_name|string|None|False|Optional name for the address object. If not provided, the address value will be used as the name|None|MaliciousHost|None|None|
|adom|string|None|False|Administrative Domain for the operation. If provided, overrides the ADOM configured in the connection|None|root|None|None|
|skip_rfc1918|boolean|True|True|Skip creation for private IP addresses as defined in RFC 1918|None|True|None|None|
|whitelist|[]string|None|False|List of addresses that should not be blocked. Supports IP addresses, CIDR ranges, and domain names|None|["198.51.100.100", "example.com", "192.0.2.0/24"]|None|None|
  
Example input:

```
{
  "address": "198.51.100.100",
  "address_object_name": "MaliciousHost",
  "adom": "root",
  "skip_rfc1918": true,
  "whitelist": [
    "198.51.100.100",
    "example.com",
    "192.0.2.0/24"
  ]
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|address_object|address_object|False|Details of the created address object|{"name": "MaliciousHost", "type": "ipmask", "subnet": "198.51.100.100/32"}|
|success|boolean|True|Boolean value indicating whether the address object was created. Returns false if the address was skipped due to whitelist or RFC 1918 filtering|True|
  
Example output:

```
{
  "address_object": {
    "name": "MaliciousHost",
    "subnet": "198.51.100.100/32",
    "type": "ipmask"
  },
  "success": true
}
```

#### Delete Address Object

This action is used to delete an address object from a FortiManager ADOM

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|address_object|string|None|True|Name of the address object to delete|None|MaliciousHost|None|None|
|adom|string|None|False|Administrative Domain for the operation. If provided, overrides the ADOM configured in the connection|None|root|None|None|
  
Example input:

```
{
  "address_object": "MaliciousHost",
  "adom": "root"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|success|boolean|True|Boolean value indicating the success of the deletion|True|
  
Example output:

```
{
  "success": true
}
```

#### Get Address Objects

This action is used to retrieve address objects from a FortiManager ADOM with optional filtering

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|adom|string|None|False|Administrative Domain to query. If provided, overrides the ADOM configured in the connection|None|root|None|None|
|fqdn_filter|string|None|False|Optional FQDN value to filter address objects (case-insensitive exact match)|None|example.com|None|None|
|name_filter|string|None|False|Optional name to filter address objects (case-insensitive exact match)|None|MaliciousHost|None|None|
|subnet_filter|string|None|False|Optional subnet value to filter address objects (case-insensitive exact match)|None|198.51.100.100/32|None|None|
  
Example input:

```
{
  "adom": "root",
  "fqdn_filter": "example.com",
  "name_filter": "MaliciousHost",
  "subnet_filter": "198.51.100.100/32"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|address_objects|[]address_object|True|List of address objects matching the specified filters|[{"name": "MaliciousHost", "type": "ipmask", "subnet": "198.51.100.100/32"}]|
  
Example output:

```
{
  "address_objects": [
    {
      "name": "MaliciousHost",
      "subnet": "198.51.100.100/32",
      "type": "ipmask"
    }
  ]
}
```

#### Get Policies

This action is used to retrieve firewall policies from a FortiManager policy package

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|adom|string|None|False|Administrative Domain for the operation. If provided, overrides the ADOM configured in the connection|None|root|None|None|
|name_filter|string|None|False|Optional policy name to filter on (case-insensitive exact match)|None|Allow Outbound|None|None|
|policy_package|string|None|True|Name of the policy package to retrieve policies from|None|default|None|None|
  
Example input:

```
{
  "adom": "root",
  "name_filter": "Allow Outbound",
  "policy_package": "default"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|policies|[]policy|True|List of firewall policies matching the specified filters|[{"policyid": 1, "name": "Allow Outbound", "srcintf": ["port1"], "dstintf": ["port2"], "srcaddr": ["all"], "dstaddr": ["all"], "service": ["ALL"], "action": "accept", "status": "enable", "schedule": "always", "logtraffic": "all"}]|
  
Example output:

```
{
  "policies": [
    {
      "action": "accept",
      "dstaddr": [
        "all"
      ],
      "dstintf": [
        "port2"
      ],
      "logtraffic": "all",
      "name": "Allow Outbound",
      "policyid": 1,
      "schedule": "always",
      "service": [
        "ALL"
      ],
      "srcaddr": [
        "all"
      ],
      "srcintf": [
        "port1"
      ],
      "status": "enable"
    }
  ]
}
```

#### Install Policy Package

This action is used to install a policy package to managed FortiGate devices or device groups

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|adom|string|None|False|Administrative Domain for the operation. If provided, overrides the ADOM configured in the connection|None|root|None|None|
|policy_package|string|None|True|Name of the policy package to install|None|default|None|None|
|target_device_groups|[]string|None|False|List of target device group names to install the policy package to. At least one target device or target device group must be provided|None|["Branch Offices"]|None|None|
|target_devices|[]string|None|False|List of target device names to install the policy package to. At least one target device or target device group must be provided|None|["FortiGate-Edge"]|None|None|
  
Example input:

```
{
  "adom": "root",
  "policy_package": "default",
  "target_device_groups": [
    "Branch Offices"
  ],
  "target_devices": [
    "FortiGate-Edge"
  ]
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|task_id|integer|True|Task identifier for the initiated install operation|512|
  
Example output:

```
{
  "task_id": 512
}
```

#### Remove Address Object from Group

This action is used to remove an address object from an address group in a FortiManager ADOM

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|address_object|string|None|True|Name of the address object to remove from the group|None|MaliciousHost|None|None|
|adom|string|None|False|Administrative Domain for the operation. If provided, overrides the ADOM configured in the connection|None|root|None|None|
|group|string|None|True|Name of the address group|None|InsightConnect Block List|None|None|
  
Example input:

```
{
  "address_object": "MaliciousHost",
  "adom": "root",
  "group": "InsightConnect Block List"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|address_objects|[]string|True|Updated list of remaining address object names in the group|["AnotherHost"]|
|success|boolean|True|Boolean value indicating the success of the operation|True|
  
Example output:

```
{
  "address_objects": [
    "AnotherHost"
  ],
  "success": true
}
```
### Triggers
  
*This plugin does not contain any triggers.*
### Tasks
  
*This plugin does not contain any tasks.*

### Custom Types
  
**address_object**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Associated Interface|string|None|False|Associated network interface|None|
|Comment|string|None|False|Optional comment|None|
|End IP|string|None|False|Range end IP (for iprange type)|None|
|FQDN|string|None|False|Fully qualified domain name (for FQDN type)|None|
|Name|string|None|True|Address object name|None|
|Start IP|string|None|False|Range start IP (for iprange type)|None|
|Subnet|string|None|False|Subnet in CIDR notation (for ipmask type)|None|
|Type|string|None|True|Address type: ipmask, FQDN, iprange|None|
  
**address_group**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Comment|string|None|False|Optional comment|None|
|Member|[]string|None|True|List of member address object names|None|
|Name|string|None|True|Address group name|None|
  
**policy**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|Action|string|None|False|Policy action: accept, deny, ipsec|None|
|Comments|string|None|False|Policy comments|None|
|Destination Address|[]string|None|False|Destination address objects or groups|None|
|Destination Interface|[]string|None|False|Destination interfaces|None|
|Log Traffic|string|None|False|Logging mode: disable, all, utm|None|
|Name|string|None|True|Policy name|None|
|Policy ID|integer|None|True|Firewall policy ID|None|
|Schedule|string|None|False|Schedule name|None|
|Service|[]string|None|False|Service objects|None|
|Source Address|[]string|None|False|Source address objects or groups|None|
|Source Interface|[]string|None|False|Source interfaces|None|
|Status|string|None|False|Policy status: enable, disable|None|


## Troubleshooting
  
*This plugin does not contain a troubleshooting.*

# Version History

* 1.0.0 - Initial plugin release

# Links

* [Fortinet FortiManager](https://www.fortinet.com/products/management/fortimanager)

## References

* [FortiManager JSON-RPC API](https://fndn.fortinet.net/)