# Create Plugin Action

Step-by-step workflow for adding a new action to an existing InsightConnect plugin.

## Prerequisites
- Identify the plugin directory under `plugins/`
- Have the vendor API documentation ready
- Know the endpoint, HTTP method, required/optional parameters, and response schema

## Steps

### 0. Build Prep (required first)
Confirm the target is **dev** or **prod** (never infer from the working directory) and run the `plugin-build-prep` skill: verify tooling and read the latest SDK version from `komand-plugin-sdk-python/README.md`. Bump `sdk.version` to that latest version as part of the spec edit. See `repos.md` for repo paths.

### 1. Read Current State
- Read `plugin.spec.yaml` to understand existing actions, types, and connection
- Read `util/` to understand the current API client structure
- Check the current version and determine the correct semver bump (Minor for new action)

### 2. Update plugin.spec.yaml
- Add the action definition with inputs, outputs, types, and examples
- Bump the version (Minor bump for new action)
- Add a `version_history` entry (no quotes around the entry)
- Ensure all outputs have `example` values
- Descriptions must NOT end with a period

### 3. Generate Scaffolding
```bash
PYENV_VERSION=3.13.x insight-plugin refresh
```
(`3.13.x` = the installed pyenv 3.13 version resolved in `plugin-build-prep`.)

### 4. Implement the Action
- Create `action.py` in the generated folder
- Use `Output.FIELD_NAME` constants for all output keys
- Access API via `self.connection.client.<domain_method>()`
- Add guards: `if not results: raise PluginException(...)`
- Wrap return in `clean()` for API response data
- Use `params.get(Input.FIELD, default)` for optional inputs

### 5. Add API Client Method
- Add a domain-specific helper to `util/api.py` or `util/graph_api_client.py`
- Method should encapsulate endpoint construction and response parsing
- Actions call helpers, never `_make_request()` directly

### 6. Write Unit Tests
- Create `unit_test/test_<action_name>.py`
- Mock at client level using `MagicMock()` on `self.connection.client`
- Test happy path + error cases
- Validate output against schema with `jsonschema.validate`
- Target ≥80% coverage

### 7. Validate
```bash
PYENV_VERSION=3.13.x prospector icon_<plugin_name>/ --without-tool pyflakes
PYENV_VERSION=3.13.x insight-plugin validate
```

### 8. Fix Any Issues
- mccabe > 10: break into helper methods
- bandit: no hardcoded secrets
- pylint: no unused imports, no imports inside functions
- Ensure all `.py` files have 644 permissions

## Quality Checks Before Committing
- [ ] All tests pass
- [ ] Prospector clean
- [ ] Plugin validates
- [ ] No `[0]` access without guards
- [ ] No bare string output keys
- [ ] version_history updated
