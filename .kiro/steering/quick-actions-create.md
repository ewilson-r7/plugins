---
inclusion: manual
---

# Creating New Quick Actions (Analyst Actions)

Quick actions are single-step plugin actions exposed in the InsightConnect UI for fast analyst enrichment. They live in `analyst_actions/` in the `rapid7/icon-built-in-steps` repository.

## File Location & Naming

- Directory: `analyst_actions/`
- Filename pattern: `{plugin}_{indicator_type}.json` (e.g., `anyrun_reputation_url.json`, `virustotal_hash.json`)
- Use underscores, all lowercase

## Required JSON Schema

Every quick action file must contain these fields:

```json
{
  "name": "User-facing name (e.g., 'URL Reputation Look Up with ANY.RUN')",
  "slug": "unique_internal_id (usually matches filename without .json)",
  "pluginName": "plugin name from plugin.spec.yaml 'name' field",
  "pluginVersion": "current version from plugin.spec.yaml 'version' field",
  "pluginVendor": "vendor from plugin.spec.yaml 'vendor' field (usually 'rapid7')",
  "pluginAction": "action name from plugin.spec.yaml 'actions' section",
  "tags": ["indicator type tag, e.g. 'IP', 'Hash', 'URL', or vendor name"],
  "inputSchema": {},
  "inputMapping": "stringified JSON with Go template vars",
  "outputExtractors": ["*"],
  "configurationRequired": false,
  "connectionRequired": true,
  "description": "What this action does",
  "isCloud": true,
  "isHidden": false
}
```

## Field Details

### name
Format: `"{Indicator Type} Look Up with {Vendor}"` or `"{Action Description} with {Vendor}"`
Examples:
- "URL Reputation Look Up with ANY.RUN"
- "IP Address Look Up with GreyNoise"
- "Agent Look Up with Crowdstrike"

### slug
Internal unique identifier. Usually `{plugin}_{action_type}`. Must be unique across all quick actions.

### pluginName / pluginVersion / pluginVendor
These must match the plugin's `plugin.spec.yaml` exactly:
- `pluginName` → `name` field in spec
- `pluginVersion` → `version` field in spec
- `pluginVendor` → `vendor` field in spec

To find these, check: `https://raw.githubusercontent.com/rapid7/insightconnect-plugins/master/plugins/{plugin_name}/plugin.spec.yaml`

### pluginAction
The exact action key from the `actions:` section of the plugin's spec YAML.

### tags
Array of strings. Common values: `"IP"`, `"Hash"`, `"URL"`, `"Domain"`, or vendor-specific like `"crowdstrike"`, `"sentinelone"`.

### inputSchema
Standard JSONSchema object describing the analyst's input form:

```json
{
  "type": "object",
  "properties": {
    "field_name": {
      "type": "string",
      "description": "Example value shown as placeholder (e.g., 'https://example.com')",
      "tooltip": "Help text for the user",
      "title": "Display label"
    }
  },
  "required": ["field_name"],
  "additionalProperties": false
}
```

Optional schema properties: `format` (e.g., `"ipv4"`), `example`, `order`.

### inputMapping
A **stringified JSON string** that maps user-provided inputs to plugin action inputs using Go template syntax `{{ .fieldName }}`. Hardcoded values can be included alongside template variables.

Examples:
- Simple: `"{\"hash\": \"{{ .hash }}\"}"` 
- With defaults: `"{\"entity_type\": \"url\", \"entity_value\": \"{{ .url }}\", \"lookup_depth\": 180}"`
- Mixed types: `"{\"address\": \"{{ .ip }}\", \"days\": \"30\", \"verbose\": true}"`

**Important:** The mapping must produce valid JSON. Non-string values (booleans, integers) should NOT be quoted.

### outputExtractors
JSONPath expressions. Use `["*"]` to extract all output fields (most common). Can specify individual fields like `["verdict", "tags"]`.

### configurationRequired / connectionRequired
- `configurationRequired`: `false` unless the action needs config beyond a connection
- `connectionRequired`: `true` if the plugin needs API keys/credentials (almost always)

### isCloud
- `true` if the action runs cloud-side (most Rapid7-vendored plugins)
- `false` if it requires a customer orchestrator

### isHidden
Always `false` unless intentionally hiding from users.

## Quick Action Design Principles

1. **Minimal inputs** — Ideally 1 field the analyst types/pastes. Hardcode sensible defaults in the inputMapping for other required plugin inputs.
2. **Fast results** — Don't use long-running actions (like sandbox submissions) unless necessary. Prefer lookups and reputation checks.
3. **No file uploads** — Quick actions shouldn't require `bytes` type inputs (file uploads are complex for the UI).
4. **Extract all output** — Use `["*"]` for outputExtractors unless output is excessively noisy.

## Branching & PR Workflow

- Create one branch per quick action: `new_qa_{plugin}_{action_type}`
- Branch off `master`
- One file per commit/PR
- PR title: `"New Quick Action: {name from JSON}"`

## Example: Complete Quick Action

```json
{
  "name": "URL Reputation Look Up with ANY.RUN",
  "slug": "anyrun_reputation_url",
  "pluginName": "any_run",
  "pluginVersion": "3.0.0",
  "pluginVendor": "rapid7",
  "pluginAction": "get_reputation",
  "tags": ["URL"],
  "inputSchema": {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "https://example.com",
        "tooltip": "URL to check reputation for",
        "title": "URL"
      }
    },
    "required": ["url"],
    "additionalProperties": false
  },
  "inputMapping": "{\"entity_type\": \"url\", \"entity_value\": \"{{ .url }}\", \"lookup_depth\": 180}",
  "outputExtractors": ["*"],
  "configurationRequired": false,
  "connectionRequired": true,
  "description": "This action is used to check the reputation of a URL using the ANY.RUN Threat Intelligence database.",
  "isCloud": true,
  "isHidden": false
}
```
