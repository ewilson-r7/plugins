---
name: create-new-plugin
description: Build a brand new Rapid7 InsightConnect plugin from scratch, covering vendor API research, plugin.spec.yaml authoring, insight-plugin scaffolding, connection and API client implementation, actions, unit tests, and validation. Use when asked to create, build, or start a new plugin, when a vendor integration does not exist yet, or when API documentation is supplied and a plugin should be built from it.
---

# Create New Plugin

Step-by-step workflow for building a brand new InsightConnect plugin from scratch.

Starting skeletons for every file below live in `references/code-templates.md`. Read the relevant
section of that file when reaching the step that needs it, rather than up front. The rules in this
file apply whether or not the template is used verbatim.

## Prerequisites
- Vendor API documentation (endpoints, auth model, request/response schemas)
- Vendor API credentials for testing
- Icon files: `icon.png` and `extension.png` (PNG format)
- Clear understanding of what actions/triggers the plugin should expose

## Steps

### 0. Build Prep (required first)
Confirm the target is **dev** or **prod** (never infer from the working directory) and run the `plugin-build-prep` skill: verify tooling is installed/current and read the latest SDK version from the top of `komand-plugin-sdk-python/README.md` changelog. Use that version for `sdk.version` below. See `repos.md` for repo paths.

### 1. Research the Vendor API
- Identify the authentication model (API key, OAuth2 client_credentials, OAuth2 auth code, basic auth)
- List the endpoints you'll need
- Note rate limits, pagination patterns, and error response formats
- Check if the API has a Python SDK (prefer raw requests unless the SDK is well-maintained)
- Determine required vs optional parameters for each endpoint

### 2. Plan the Plugin
- Choose a plugin name (snake_case, matches vendor name): e.g., `crowdstrike_falcon`
- Decide on actions (1:1 with API operations you want to expose)
- Define custom types for complex response objects
- Identify shared constants (base URL, timeout, error map)

### 3. Write plugin.spec.yaml
Create `plugins/<plugin_name>/plugin.spec.yaml`. Skeleton: `references/code-templates.md`,
"plugin.spec.yaml" section. Then add connection, types, and actions sections.

Key rules:
- Descriptions must NOT end with a period
- All outputs need `example` values
- Mark inputs `required: true` when the vendor API requires them
- Use single-line strings for descriptions (no `>` or `|` block scalars)
- Add `placeholder` for free-form string inputs
- Add `enum` for fixed value sets
- Add `order` to control input display sequence

### 4. Scaffold the Plugin
```bash
cd plugins/
PYENV_VERSION=3.13.x insight-plugin create
```
This generates the full directory structure from your spec. (`3.13.x` = the installed pyenv 3.13 version resolved in `plugin-build-prep` via `pyenv versions`.)

### 5. Create requirements.txt
```
# Only add dependencies NOT already in the SDK
# The SDK includes: requests, jsonschema, insightconnect-plugin-runtime
# Pin all versions exactly
```
Leave empty if no additional dependencies are needed.

### 6. Implement Connection (connection/connection.py)
Skeleton: `references/code-templates.md`, "connection/connection.py" section.

Rules:
- `connect()` only stores state and instantiates clients — NO API calls
- `test()` validates credentials
- Auth logic belongs in the API client, not here
- Use modern `super().__init__()`

### 7. Implement API Client (util/api.py)
Skeleton: `references/code-templates.md`, "util/api.py" section.

Rules:
- Use plain `requests.request()` — never store a `requests.Session` in the class (stored sessions cause issues with long-lived plugin processes; see `common-mistakes.md` #25)
- Central `_make_request()` with timeout + connection error handling
- `_handle_response()` maps HTTP status codes via `HTTP_ERROR_MAP`
- Domain-specific public methods (actions call these, not `_make_request`)
- Handle 401 with single-retry token refresh pattern
- Parse JSON with fallback to PluginException

### 8. Create Constants (util/constants.py)
Skeleton: `references/code-templates.md`, "util/constants.py" section. It carries `TIMEOUT`,
`DEFAULT_MAX_RESULTS`, and the `HTTP_ERROR_MAP` that `_handle_response()` reads.

### 9. Implement Actions
For each action in `icon_<plugin_name>/actions/<name>/action.py`. Skeleton:
`references/code-templates.md`, "actions/<name>/action.py" section.

Rules:
- Use `Output.FIELD_NAME` constants
- Guard list/dict access before indexing
- Wrap API responses in `clean()` to strip None values
- Use `params.get(Input.FIELD, default)` for optional inputs

### 10. Write Unit Tests
Create `unit_test/util.py` with the shared mocks, then one test file per action. Skeletons:
`references/code-templates.md`, "unit_test/util.py" and "unit_test/test_<action>.py" sections.

### 11. Add Icon Files
- `icon.png` — plugin icon (vendor logo, square, transparent background)
- `extension.png` — extension icon (same or variant)

### 12. Validate
```bash
PYENV_VERSION=3.13.x prospector icon_<plugin_name>/ --without-tool pyflakes
PYENV_VERSION=3.13.x insight-plugin validate
find . -name "*.py" -perm 600 -exec chmod 644 {} \;
```

### 13. Integration Test
```bash
# Create a test JSON in tests/ directory
PYENV_VERSION=3.13.x insight-plugin run tests/<action_name>.json
```

## Version Rules for New Plugins
- Keep at `1.0.0` throughout development
- Do NOT bump version until after initial production release
- First release is always `1.0.0`

## Final Checklist
- [ ] `plugin.spec.yaml` complete with all fields
- [ ] All actions implemented with guards and clean()
- [ ] API client with proper error handling and domain methods
- [ ] Constants file with TIMEOUT and HTTP_ERROR_MAP
- [ ] Unit tests for every action (≥80% coverage)
- [ ] Prospector clean (0 issues)
- [ ] `insight-plugin validate` passes
- [ ] File permissions correct (644 on all .py files)
- [ ] No hardcoded credentials in test files
- [ ] Icon files present
- [ ] requirements.txt exists (even if empty)
