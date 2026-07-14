import json
import logging
import os
from unittest.mock import MagicMock

import insightconnect_plugin_runtime

from komand_chatgpt.connection.connection import Connection
from komand_chatgpt.connection.schema import Input as ConnectionInput


STUB_CONNECTION_PARAMS = {
    ConnectionInput.API_KEY: {"secretKey": "sk-proj-test-key-1234567890"},
    ConnectionInput.MODEL: "gpt-4o",
}


class MockConnection:
    """Provides a mock connection with a mock ChatGPT client."""

    def __init__(self):
        self.client = MagicMock()
        self.logger = logging.getLogger("test_connection")


def create_mock_action(action_class):
    """Create an action instance with a mocked connection."""
    action = action_class()
    action.connection = MockConnection()
    action.logger = logging.getLogger("test_action")
    return action


def load_fixture(filename: str) -> dict:
    """Load a JSON fixture from the responses directory."""
    fixture_path = os.path.join(os.path.dirname(__file__), "responses", filename)
    with open(fixture_path, "r") as fixture_file:
        return json.load(fixture_file)
