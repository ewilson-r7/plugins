import json
import os
import logging
from unittest.mock import MagicMock

RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "responses")


def load_response(filename: str) -> dict:
    """Load a JSON fixture file from the responses directory."""
    filepath = os.path.join(RESPONSES_DIR, filename)
    with open(filepath) as fh:
        return json.load(fh)


class MockResponse:
    """Minimal stand-in for a requests.Response object."""

    def __init__(self, json_data, status_code: int = 200, headers: dict = None):
        self._json_data = json_data
        self.status_code = status_code
        self.headers = headers or {"X-Rl": "44", "X-Ttl": "60"}
        self.text = json.dumps(json_data)

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            from requests import HTTPError

            raise HTTPError(response=self)


def default_connector(action):
    """
    Wire up an action with a real Connection (no params) and an ApiClient backed
    by a real requests.Session (which tests will patch at the Session.request level).
    """
    from icon_ip_api.connection.connection import Connection
    from icon_ip_api.util.api import ApiClient

    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)

    connection = Connection()
    connection.logger = logger
    connection.connect(params={})

    action.connection = connection
    action.logger = logger

    return action
