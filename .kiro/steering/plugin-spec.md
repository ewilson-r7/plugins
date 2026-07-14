---
inclusion: fileMatch
fileMatchPattern: "**/plugin.spec.yaml"
---
# plugin.spec.yaml — Reference

`plugin.spec.yaml` is the **source of truth**. All auto-generated files derive from it.

## Spec Structure

```yaml
plugin_spec_version: v2
extension: plugin
products: [insightconnect]
name: plugin_name                  # snake_case, must match directory name
title: Human Readable Title
description: One-sentence description.
version: 1.0.0
cloud_ready: false
vendor: rapid7
support: rapid7
status: []
supported_versions: ["YYYY-MM-DD"] # REQUIRED — date vendor API was last verified
sdk:
  type: full
  version: 6.6.0
  user: nobody
key_features: ["Brief feature description"]
requirements: ["API credentials", "Base URL"]
version_history:                   # REQUIRED
  - "1.0.0 - Initial plugin release"
resources:
  source_url: https://github.com/rapid7/insightconnect-plugins/tree/master/plugins/plugin_name
  license_url: https://github.com/rapid7/insightconnect-plugins/blob/master/LICENSE
  vendor_url: https://vendor.example.com
links: ["[Vendor](https://vendor.example.com)"]
references: ["[API Docs](https://vendor.example.com/api)"]
tags: [tag1, tag2]
hub_tags:
  use_cases: [threat_detection_and_response]
  keywords: [keyword1]
  features: []
```

## Types, Connection, Actions, Triggers, Tasks

```yaml
types:
  my_type:
    field_one: {title: Field One, type: string, required: false}

connection:  # omit entirely for unauthenticated APIs
  api_key: {title: API Key, type: credential_secret_key, required: true, order: 1}

actions:
  get_item:
    title: Get Item
    description: Retrieve an item by ID
    input:
      item_id: {title: Item ID, type: string, example: "12345", required: true}
    output:
      item: {title: Item, type: my_type, required: false}

triggers:
  new_alert:
    title: New Alert
    input:
      poll_interval: {title: Poll Interval, type: integer, default: 60, required: false}
    output:
      alert: {title: Alert, type: object, required: false}

tasks:
  monitor_events:
    title: Monitor Events
    output:
      events: {title: Events, type: "[]object", required: false}
```

## Field Types
- **Scalar**: `string`, `integer`, `float`, `boolean`, `bytes`, `date`, `password`
- **Complex**: `object`, `[]string`, `[]integer`, `[]object`, `[]my_custom_type`
- **Credential**: `credential_secret_key`, `credential_username_password`, `credential_asymmetric_key`

## Field Properties
`title`, `description`, `type` (all required), `required`, `example`, `default`, `placeholder`, `tooltip`, `order`, `enum`

### UX Guidance for Inputs
- **`placeholder`**: Always add for free-form string inputs — shows greyed-out hint text in the empty field (e.g. `placeholder: "osPlatform eq 'Windows10'"`)
- **`tooltip`**: Add when the input requires context beyond the description — appears as a hover/info popup. Link to vendor docs when the input accepts a query language or complex syntax (e.g. OData filters, JQL, KQL)
- **`enum`**: Use when the input has a **small, stable** set of valid values — renders as a dropdown. **Avoid enums for large or vendor-managed lists** (e.g., URL categories, rule types) that change over time or include customer-defined values. Use a free-text string instead and resolve names via the API at runtime.
- **`default`**: Use for optional inputs where a sensible default improves usability
- **`order`**: Use to control display order when input sequence matters for the user

## Spec Descriptions
- Avoid nested double quotes in `description` fields — the generated `schema.py` will have a syntax error. Use single quotes or rephrase instead.
  ```yaml
  # BAD — nested quotes break schema.py generation
  description: 'Supports categories (e.g., "News and Media")'
  
  # GOOD — no nested quotes
  description: Supports both predefined and custom categories
  ```

## Credential Access
- `credential_secret_key`: `params.get(Input.FIELD, {}).get("secretKey", "")`
- `credential_username_password`: `.get("username")` and `.get("password")`
