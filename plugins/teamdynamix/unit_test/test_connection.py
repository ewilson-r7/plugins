"""Unit tests for the TeamDynamix Connection."""

import unittest
from unittest.mock import patch

from insightconnect_plugin_runtime.exceptions import ConnectionTestException

from icon_teamdynamix.connection.connection import Connection
from unit_test.util import STUB_CONNECTION_PARAMS, MockResponse, AUTH_TOKEN


class TestConnection(unittest.TestCase):
    def _make_connection(self) -> Connection:
        import logging

        conn = Connection()
        conn.logger = logging.getLogger("test_connection")
        conn.connect(STUB_CONNECTION_PARAMS)
        conn.client._token = AUTH_TOKEN
        return conn

    @patch("requests.Session.request")
    def test_connection_test_success(self, mock_request):
        """test() returns success dict when the search API responds 200."""
        mock_request.return_value = MockResponse(200, "search_tickets_empty.json")
        conn = self._make_connection()
        result = conn.test()
        self.assertEqual(result, {"success": True})

    @patch("requests.Session.request")
    def test_connection_test_failure_raises_connection_test_exception(self, mock_request):
        """test() raises ConnectionTestException when the API returns an error."""
        mock_request.return_value = MockResponse(401)
        conn = self._make_connection()
        with self.assertRaises(ConnectionTestException):
            conn.test()

    @patch("requests.Session.post")
    def test_authenticate_success(self, mock_post):
        """_authenticate() returns a token string on 200."""
        import logging

        mock_post.return_value = MockResponse(200, text=f'"{AUTH_TOKEN}"')
        conn = Connection()
        conn.logger = logging.getLogger("test_connection")
        conn.connect(STUB_CONNECTION_PARAMS)
        # Clear the injected token to force authentication
        conn.client._token = None
        token = conn.client._authenticate()
        self.assertEqual(token, AUTH_TOKEN)

    @patch("requests.Session.post")
    def test_authenticate_failure_raises_plugin_exception(self, mock_post):
        """_authenticate() raises PluginException when credentials are rejected."""
        import logging
        from insightconnect_plugin_runtime.exceptions import PluginException

        mock_post.return_value = MockResponse(401, text="Unauthorized")
        conn = Connection()
        conn.logger = logging.getLogger("test_connection")
        conn.connect(STUB_CONNECTION_PARAMS)
        conn.client._token = None
        with self.assertRaises(PluginException):
            conn.client._authenticate()

    @patch("requests.Session.post")
    def test_authenticate_empty_token_raises_plugin_exception(self, mock_post):
        """_authenticate() raises PluginException when the API returns an empty token."""
        import logging
        from insightconnect_plugin_runtime.exceptions import PluginException

        mock_post.return_value = MockResponse(200, text='""')
        conn = Connection()
        conn.logger = logging.getLogger("test_connection")
        conn.connect(STUB_CONNECTION_PARAMS)
        conn.client._token = None
        with self.assertRaises(PluginException):
            conn.client._authenticate()
