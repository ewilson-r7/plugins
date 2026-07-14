---
inclusion: manual
---

# Updating Quick Actions (Analyst Actions)

Quick actions must be kept in sync with the plugins they reference. The primary reason to update a quick action is when a plugin has released a new version that changes the version number or modifies action inputs/outputs.

## When to Update

- Plugin version has been bumped (new release)
- Plugin action inputs have changed (renamed, added required fields, removed fields)
- Plugin action has been renamed or deprecated
- Plugin vendor field has changed

## Update Process

### 1. Find the Current Plugin Version

Fetch the plugin's latest spec:
```
https://raw.githubusercontent.com/rapid7/insightconnect-plugins/master/plugins/{pluginName}/plugin.spec.yaml
```

Check the `version` field at the top of the spec.

### 2. Compare Action Inputs

Look at the `actions:` section in the plugin spec for the action referenced by `pluginAction`. Compare the **required inputs** and their names/types against what the quick action's `inputMapping` expects.

Key things to verify:
- All input field names in the `inputMapping` still exist in the plugin action's `input` section
- No new **required** inputs have been added that aren't accounted for in the mapping
- Field types haven't changed (e.g., string → integer)
- Enum values are still valid if hardcoded in the mapping

### 3. Update the Quick Action JSON

Fields to update:

| Field | What to check |
|-------|--------------|
| `pluginVersion` | Must match current `version` in plugin.spec.yaml |
| `inputMapping` | Must map to valid input field names for the action |
| `inputSchema` | Update descriptions/tooltips if the plugin's input descriptions changed |
| `pluginAction` | Update if the action was renamed |

### 4. Verify the inputMapping Still Produces Valid JSON

The mapping must:
- Reference only fields that exist in the plugin action's `input` section
- Use correct types (strings quoted, booleans/integers unquoted)
- Include any new required fields with sensible defaults

### Example: Version Bump Only

If the plugin went from `5.1.0` to `5.2.0` with no input changes:

```diff
- "pluginVersion": "5.1.0",
+ "pluginVersion": "5.2.0",
```

### Example: Input Field Renamed

If the plugin renamed `address` to `ip_address`:

```diff
- "inputMapping": "{\"address\": \"{{ .ip }}\", \"days\": \"30\", \"verbose\": true}",
+ "inputMapping": "{\"ip_address\": \"{{ .ip }}\", \"days\": \"30\", \"verbose\": true}",
```

### Example: New Required Input Added

If the plugin added a required `api_version` field:

```diff
- "inputMapping": "{\"hash\": \"{{ .hash }}\"}",
+ "inputMapping": "{\"hash\": \"{{ .hash }}\", \"api_version\": \"v2\"}",
```

Hardcode the new required field to a sensible default — don't add it to the `inputSchema` unless the analyst needs to choose.

## Branching & PR Workflow

- Branch name: `update_qa_{plugin}_{action_type}` or reference a ticket like `SOAR-XXXXX`
- Branch off `master`
- PR title: `"Update {slug} plugin version"` or similar descriptive title

## Bulk Updates

When a plugin releases a major version, multiple quick actions may reference it. Check all files:

```bash
grep -l '"pluginName": "{plugin_name}"' analyst_actions/*.json
```

Update each file's `pluginVersion` and verify `inputMapping` compatibility. These can go in a single branch/PR if they're all for the same plugin version bump.

## Checklist

- [ ] `pluginVersion` matches current version in plugin.spec.yaml
- [ ] `pluginAction` still exists in the plugin spec's `actions` section
- [ ] All fields referenced in `inputMapping` exist in the plugin action's `input` section
- [ ] No new required plugin inputs are missing from the mapping
- [ ] `inputMapping` produces valid JSON (proper quoting, escaping)
- [ ] `pluginVendor` still matches the plugin spec's `vendor` field
