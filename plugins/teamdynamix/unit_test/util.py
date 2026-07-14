"""Shared test helpers for TeamDynamix plugin unit tests."""

import json
import logging
import os

import insightconnect_plugin_runtime

from icon_teamdynamix.connection.connection import Connection
from icon_teamdynamix.connection.schema import Input

STUB_CONNECTION_PARAMS = {
    Input.BASE_URL: "https://yourorg.teamdynamix.com",
    Input.BEID: "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    Input.WEB_SERVICES_KEY: {"secretKey": "ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj"},
    Input.APP_ID: 42,
}

AUTH_TOKEN = "stubtoken123"


class MockResponse:
    """Simulates a requests.Response object for unit tests."""

    def __init__(self, status_code: int, filename: str = None, text: str = ""):
        self.status_code = status_code
        if filename:
            filepath = os.path.join(os.path.dirname(__file__), "responses", filename)
            with open(filepath) as fh:
                self.text = fh.read()
        else:
            self.text = text

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def default_connector(action: insightconnect_plugin_runtime.Action) -> insightconnect_plugin_runtime.Action:
    """Wire a configured Connection to *action* and return it.

    The TeamDynamix client authenticates lazily (first API call), so we patch
    _authenticate at the call sites in tests rather than here.
    """
    connection = Connection()
    connection.logger = logging.getLogger("test_connection")
    connection.connect(STUB_CONNECTION_PARAMS)
    action.connection = connection
    action.logger = logging.getLogger("test_action")
    return action
