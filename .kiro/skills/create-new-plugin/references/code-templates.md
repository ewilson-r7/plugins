# Code Templates for a New Plugin

Starting skeletons for each file in a new InsightConnect plugin. Read the section for the step
being worked on rather than the whole file. The rules that govern each template stay in
`SKILL.md`, since they apply whether or not the template is used verbatim.

Every identifier here is a placeholder. Substitute the real vendor name, endpoints, and fields.

## plugin.spec.yaml

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

Connection, types, and actions sections are added below this.

## connection/connection.py

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

## util/api.py

```python
class VendorApiClient:
    def __init__(self, api_key, base_url, logger):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._logger = logger

    def _get_headers(self):
        return {"Authorization": f"Bearer {self._api_key}"}

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self._base_url}{endpoint}"
        try:
            response = requests.request(
                method, url, headers=self._get_headers(), timeout=TIMEOUT, **kwargs
            )
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

## util/constants.py

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

## actions/<name>/action.py

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

## unit_test/util.py

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

## unit_test/test_<action>.py

One file per action.

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
