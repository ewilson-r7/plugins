import json
import os
import logging
import insightconnect_plugin_runtime
from icon_halo_itsm.connection.connection import Connection
from icon_halo_itsm.connection.schema import Input

STUB_CONNECTION_PARAMS = {
    Input.BASE_URL: "https://example.haloitsm.com",
    Input.CLIENT_ID: "test-client-id",
    Input.CLIENT_SECRET: {"secretKey": "test-client-secret"},
    Input.TENANT: "test-tenant",
}

STUB_AUTH_RESPONSE = {
    "access_token": "test-access-token",
    "token_type": "Bearer",
    "expires_in": 3600,
}


class MockResponse:
    def __init__(self, status_code: int, filename: str = None, json_data=None):
        self.status_code = status_code
        self.text = ""
        if filename:
            filepath = os.path.join(os.path.dirname(__file__), "responses", filename)
            with open(filepath) as f:
                self.text = f.read()
        elif json_data is not None:
            self.text = json.dumps(json_data)

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def mock_auth_response(*args, **kwargs):
    """Return a mock successful auth response."""
    return MockResponse(200, json_data=STUB_AUTH_RESPONSE)


def default_connector(action: insightconnect_plugin_runtime.Action):
    """Attach a configured Connection to the given action."""
    connection = Connection()
    connection.logger = logging.getLogger("test_connection")
    connection.connect(STUB_CONNECTION_PARAMS)
    action.connection = connection
    action.logger = logging.getLogger("test_action")
    return action
