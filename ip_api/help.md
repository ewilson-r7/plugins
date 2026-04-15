# Description

Geolocate IPv4 addresses, IPv6 addresses, and domain names using the ip-api.com service

# Key Features

* Geolocate a single IP address or domain name
* Geolocate up to 100 IPs or domains in a single batch request

# Requirements

* No API key required
* Rate limit of 45 requests/minute for single lookups
* Rate limit of 15 requests/minute for batch lookups

# Supported Product Versions
  
*This plugin does not contain any supported product versions.*

# Documentation

## Setup

The connection configuration accepts the following parameters:  

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

Example input:

```
{}
```

## Technical Details

### Actions


#### Geolocate Bulk

This action is used to look up geolocation data for up to 100 IPv4 addresses, IPv6 addresses, or domain names in a 
single request

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|lang|string|en|False|Language for localized city and country names|["en", "de", "es", "pt-BR", "fr", "ja", "zh-CN", "ru"]|en|None|None|
|queries|[]string|None|True|List of IPv4 addresses, IPv6 addresses, or domain names to look up (maximum 100)|None|["8.8.8.8", "1.1.1.1"]|None|None|
  
Example input:

```
{
  "lang": "en",
  "queries": [
    "8.8.8.8",
    "1.1.1.1"
  ]
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|results|[]geolocation_result|False|List of geolocation results for the queried IPs or domains|None|
  
Example output:

```
{
  "results": [
    {
      "AS Name": {},
      "AS Number": {},
      "City": {},
      "Continent": {},
      "Continent Code": {},
      "Country": {},
      "Country Code": {},
      "Currency": {},
      "District": {},
      "Hosting": {},
      "ISP": {},
      "Latitude": 0.0,
      "Longitude": {},
      "Message": {},
      "Mobile": "true",
      "Organization": {},
      "Proxy": {},
      "Query": {},
      "Region": {},
      "Region Name": {},
      "Reverse DNS": {},
      "Status": "",
      "Timezone": {},
      "UTC Offset": 0,
      "ZIP Code": {}
    }
  ]
}
```

#### Geolocate IP

This action is used to look up geolocation data for a single IPv4 address, IPv6 address, or domain name

##### Input

|Name|Type|Default|Required|Description|Enum|Example|Placeholder|Tooltip|
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
|lang|string|en|False|Language for localized city and country names|["en", "de", "es", "pt-BR", "fr", "ja", "zh-CN", "ru"]|en|None|None|
|query|string|None|True|IPv4 address, IPv6 address, or domain name to look up|None|8.8.8.8|None|None|
  
Example input:

```
{
  "lang": "en",
  "query": "8.8.8.8"
}
```

##### Output

|Name|Type|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- |
|result|geolocation_result|False|Geolocation result for the queried IP or domain|None|
  
Example output:

```
{
  "result": {
    "AS Name": {},
    "AS Number": {},
    "City": {},
    "Continent": {},
    "Continent Code": {},
    "Country": {},
    "Country Code": {},
    "Currency": {},
    "District": {},
    "Hosting": {},
    "ISP": {},
    "Latitude": 0.0,
    "Longitude": {},
    "Message": {},
    "Mobile": "true",
    "Organization": {},
    "Proxy": {},
    "Query": {},
    "Region": {},
    "Region Name": {},
    "Reverse DNS": {},
    "Status": "",
    "Timezone": {},
    "UTC Offset": 0,
    "ZIP Code": {}
  }
}
```
### Triggers
  
*This plugin does not contain any triggers.*
### Tasks
  
*This plugin does not contain any tasks.*

### Custom Types
  
**geolocation_result**

|Name|Type|Default|Required|Description|Example|
| :--- | :--- | :--- | :--- | :--- | :--- |
|AS Number|string|None|False|AS number and name (e.g. AS15169 Google LLC)|None|
|AS Name|string|None|False|AS name (RIR)|None|
|City|string|None|False|City name|None|
|Continent|string|None|False|Continent name|None|
|Continent Code|string|None|False|Two-letter continent code|None|
|Country|string|None|False|Country name|None|
|Country Code|string|None|False|Two-letter country code (ISO 3166-1 alpha-2)|None|
|Currency|string|None|False|National currency|None|
|District|string|None|False|District name|None|
|Hosting|boolean|None|False|Hosting, colocated, or data center|None|
|ISP|string|None|False|Internet Service Provider name|None|
|Latitude|float|None|False|Latitude|None|
|Longitude|float|None|False|Longitude|None|
|Message|string|None|False|Failure reason when status is fail|None|
|Mobile|boolean|None|False|Mobile (cellular) connection|None|
|UTC Offset|integer|None|False|Timezone UTC DST offset in seconds|None|
|Organization|string|None|False|Organization name|None|
|Proxy|boolean|None|False|Proxy, VPN, or Tor exit address|None|
|Query|string|None|False|IP address or domain used in the query|None|
|Region|string|None|False|Region or state code|None|
|Region Name|string|None|False|Region or state name|None|
|Reverse DNS|string|None|False|Reverse DNS of the IP|None|
|Status|string|None|False|Query status, either success or fail|None|
|Timezone|string|None|False|City timezone (tz database format)|None|
|ZIP Code|string|None|False|ZIP or postal code|None|


## Troubleshooting
  
*This plugin does not contain a troubleshooting.*

# Version History
  
*This plugin does not contain a version history.*

# Links
  
*This plugin does not contain any links.*

## References
  
*This plugin does not contain any references.*