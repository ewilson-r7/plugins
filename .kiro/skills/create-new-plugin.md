# Create New Plugin

Step-by-step workflow for building a brand new InsightConnect plugin from scratch.

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
Create `plugins/<plugin_name>/plugin.spec.yaml` with:

```yaml
plugin_spec_version: v2
extension: plugin
products: [insightconnect]
name: plugin_name
title: Human Readable Title
description: One-sentence description without trailing period
version: 1.0.0
connection_version: 1
supported_versions: [Vendor API vX.Y YYYY-MM-DD]
vendor: rapid7
support: rapid7
status: []
cloud_ready: true
sdk:
  type: slim
  version: <latest>   # from top of komand-plugin-sdk-python/README.md changelog (see plugin-build-prep)
  user: nobody
key_features:
- Feature one
- Feature two
requirements:
- Requirement one
version_history:
- 1.0.0 - Initial plugin release
resources:
  source_url: https://github.com/rapid7/insightconnect-plugins/tree/master/plugins/plugin_name
  license_url: https://github.com/rapid7/insightconnect-plugins/blob/master/LICENSE
  vendor_url: https://vendor.example.com
tags:
- tag1
- tag2
hub_tags:
  use_cases: [threat_detection_and_response]
  keywords: [keyword1, keyword2]
  features: []
```

Add connection, types, and actions sections. Key rules:
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
```python
class Connection(insightconnect_plugin_runtime.Connection):
    def __init__(self):
        super().__init__(input=ConnectionSchema())
        self.client = None

    def connect(self, params):  # pylint: disable=signature-differs
        api_key = params.get(Input.API_KEY, {}).get("secretKey", "").strip()
        base_url = params.get(Input.BASE_URL, "").strip()

        self.client = VendorApiClient(
            api_key=api_key,
            base_url=base_url,
            logger=self.logger,
        )

    def test(self):
        try:
            self.client.authenticate()
        except PluginException as error:
            raise ConnectionTestException(
                cause=error.cause, assistance=error.assistance, data=error.data
            ) from error
        return {"success": True}
```

Rules:
- `connect()` only stores state and instantiates clients — NO API calls
- `test()` validates credentials
- Auth logic belongs in the API client, not here
- Use modern `super().__init__()`

### 7. Implement API Client (util/api.py)
```python
class VendorApiClient:
    def __init__(self, api_key, base_url, logger):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._logger = logger
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {api_key}"})

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self._base_url}{endpoint}"
        try:
            response = self._session.request(method, url, timeout=TIMEOUT, **kwargs)
        except requests.exceptions.Timeout as error:
            raise PluginException(cause="Request timed out", ...) from error
        except requests.exceptions.ConnectionError as error:
            raise PluginException(cause="Unable to connect", ...) from error
        return self._handle_response(response)

    # Domain-specific helpers
    def get_device(self, device_id):
        return self._make_request("GET", f"/devices/{device_id}")

    def list_alerts(self, severity=None, limit=25):
        params = {"limit": limit}
        if severity:
            params["severity"] = severity
        return self._make_request("GET", "/alerts", params=params)
```

Rules:
- Central `_make_request()` with timeout + connection error handling
- `_handle_response()` maps HTTP status codes via `HTTP_ERROR_MAP`
- Domain-specific public methods (actions call these, not `_make_request`)
- Handle 401 with single-retry token refresh pattern
- Parse JSON with fallback to PluginException

### 8. Create Constants (util/constants.py)
```python
TIMEOUT = 30
DEFAULT_MAX_RESULTS = 25

HTTP_ERROR_MAP = {
    400: {"cause": "Bad request", "assistance": "Verify inputs are correct."},
    401: {"cause": "Unauthorized", "assistance": "Verify API credentials."},
    403: {"cause": "Forbidden", "assistance": "Verify account permissions."},
    404: {"cause": "Resource not found", "assistance": "Verify the ID is correct."},
    429: {"cause": "Rate limit exceeded", "assistance": "Wait and try again."},
    500: {"cause": "Internal server error", "assistance": "Try again later."},
    503: {"cause": "Service unavailable", "assistance": "Try again later."},
}
```

### 9. Implement Actions
For each action in `icon_<plugin_name>/actions/<name>/action.py`:

```python
class GetDevice(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super().__init__(name="get_device", description=Component.DESCRIPTION,
                         input=GetDeviceInput(), output=GetDeviceOutput())

    def run(self, params={}):
        device_id = params.get(Input.DEVICE_ID)

        device = self.connection.client.get_device(device_id)
        if not device:
            raise PluginException(
                cause="Device not found.",
                assistance=f"Please verify device ID '{device_id}' is correct.",
            )

        return {Output.DEVICE: clean(device)}
```

Rules:
- Use `Output.FIELD_NAME` constants
- Guard list/dict access before indexing
- Wrap API responses in `clean()` to strip None values
- Use `params.get(Input.FIELD, default)` for optional inputs

### 10. Write Unit Tests
Create `unit_test/util.py`:
```python
from unittest.mock import MagicMock

class MockApiClient:
    def __init__(self):
        self.get_device = MagicMock()
        self.list_alerts = MagicMock()
        self.authenticate = MagicMock()

class MockConnection:
    def __init__(self):
        self.client = MockApiClient()

class Util:
    @staticmethod
    def default_connector(action):
        action.connection = MockConnection()
        action.connection.logger = logging.getLogger("connection")
        action.logger = logging.getLogger("action")
        return action
```

Create one test file per action:
```python
class TestGetDevice(TestCase):
    def setUp(self):
        self.action = Util.default_connector(GetDevice())

    def test_get_device_success(self):
        self.action.connection.client.get_device.return_value = {"id": "123", "name": "laptop"}
        result = self.action.run({Input.DEVICE_ID: "123"})
        self.assertEqual(result["device"]["id"], "123")
        validate(result, GetDeviceOutput.schema)
```

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
