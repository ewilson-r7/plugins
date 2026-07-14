import json
import logging
import os
from unittest.mock import MagicMock, patch

from icon_fortinet_fortimanager.connection.connection import Connection

STUB_CONNECTION_PARAMS = {
    "hostname": "fortimanager.example.com",
    "authentication_type": "API Token",
    "api_key": {"secretKey": "test-api-key-12345"},
    "ssl_verify": False,
    "adom": "root",
}

STUB_SESSION_CONNECTION_PARAMS = {
    "hostname": "fortimanager.example.com",
    "authentication_type": "Session-Based",
    "username": "admin",
    "password": {"secretKey": "test-password-123"},
    "ssl_verify": False,
    "adom": "root",
}

PAYLOADS_DIR = os.path.join(os.path.dirname(__file__), "payloads")


def load_payload(filename: str) -> dict:
    """Load a JSON payload from the payloads directory."""
    filepath = os.path.join(PAYLOADS_DIR, filename)
    with open(filepath, "r") as f:
        return json.load(f)


class MockResponse:
    """Mock requests Response object."""

    def __init__(self, json_data: dict, status_code: int = 200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            from requests.exceptions import HTTPError

            raise HTTPError(response=self)


def create_mock_connection(logger=None):
    """Create a Connection instance with stored parameters (no API calls)."""
    if logger is None:
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)

    connection = Connection()
    connection.logger = logger
    connection.connect(STUB_CONNECTION_PARAMS)
    return connection


def create_mock_session_connection(logger=None):
    """Create a Connection instance with session-based auth parameters."""
    if logger is None:
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)

    connection = Connection()
    connection.logger = logger
    connection.connect(STUB_SESSION_CONNECTION_PARAMS)
    return connection
