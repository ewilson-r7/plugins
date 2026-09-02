# Plugin Review & Questions (Read-Only)

Workflow for reviewing a plugin or answering questions about one. This is **read-only** — no file edits, no branches, no `insight-plugin refresh/create`.

## Source of Truth: Master Repos Only
Always read from a master repo, never from the dev fork (the fork may hold uncommitted local changes):
- **Current plugins** → `~/Documents/GitHub/insightconnect-plugins/plugins/<name>`
- **Legacy plugins** → `~/Documents/GitHub/komand-plugins/plugins/<name>`

If unsure, check `insightconnect-plugins` first, then fall back to `komand-plugins`.

## Steps

### 1. Locate the plugin
```bash
ls ~/Documents/GitHub/insightconnect-plugins/plugins/<name> \
  || ls ~/Documents/GitHub/komand-plugins/plugins/<name>
```

### 2. Read the relevant files
- `plugin.spec.yaml` — actions/triggers/tasks, connection, version, SDK version
- `icon_<name>/connection/connection.py` — auth model
- `icon_<name>/util/` — API client, constants, error handling
- `icon_<name>/actions/*/action.py` — action logic
- `unit_test/` — coverage of behaviors

### 3. Analyze against conventions
Use the same standards the build agent enforces (see `common-mistakes.md`, `implementation.md`, `exceptions.md`, `prospector.md`, `testing.md`). Common review points:
- `connect()` makes no API calls; `test()` validates
- Credentials `.strip()`'d; auth logic in the client, not connection
- `Output.FIELD_NAME` constants (no bare string keys)
- Guards before `[0]` list access
- `clean()` wrapping API responses
- `PluginException`/`ConnectionTestException` (never raw `Exception`)
- Version-pinned `requirements.txt`
- `HTTP_ERROR_MAP` coverage (400/401/403/404/429/500/503)
- Test coverage ≥80%, mocked at the right level
- SDK version vs the latest in `komand-plugin-sdk-python/README.md`

### 4. Report findings
Summarize what the plugin does, its auth model, and any gaps or risks. Prioritize actionable items. Do not modify anything.

## If the Review Leads to a Fix
Stop. Confirm the user wants a change, ask **prod or dev**, then switch to build intent (`plugin-build-prep` → `create-plugin-action` / etc.). Never edit the master repo in place during a review.
