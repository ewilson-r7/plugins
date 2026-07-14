import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

import requests.exceptions
from insightconnect_plugin_runtime.exceptions import ConnectionTestException

from unit_test.util import (
    MockResponse,
    create_mock_connection,
    create_mock_session_connection,
    load_payload,
)


class TestConnection(TestCase):
    def setUp(self):
        self.system_status_response = load_payload("system_status.json.resp")
        self.login_success_response = load_payload("login_success.json.resp")
        self.login_failure_response = load_payload("login_failure.json.resp")
        self.session_expired_response = load_payload("error_session_expired.json.resp")

    @patch("requests.Session.post")
    def test_connection_test_api_token_success(self, mock_post):
        """Test successful connection test with API Token authentication."""
        connection = create_mock_connection()
        mock_post.return_value = MockResponse(self.system_status_response)

        result = connection.test()

        self.assertEqual(result, {"success": True})
        mock_post.assert_called_once()

    @patch("requests.Session.post")
    def test_connection_test_session_based_success(self, mock_post):
        """Test successful connection test with Session-Based authentication."""
        connection = create_mock_session_connection()

        # First call: login (returns session token), Second call: logout
        logout_response = {
            "id": 2,
            "result": [{"status": {"code": 0, "message": "OK"}}],
        }
        mock_post.side_effect = [
            MockResponse(self.login_success_response),
            MockResponse(logout_response),
        ]

        result = connection.test()

        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_post.call_count, 2)

    @patch("requests.Session.post")
    def test_connection_test_invalid_credentials_raises_exception(self, mock_post):
        """Test that invalid credentials raise ConnectionTestException."""
        connection = create_mock_session_connection()
        mock_post.return_value = MockResponse(self.login_failure_response)

        with self.assertRaises(ConnectionTestException) as context:
            connection.test()

        self.assertIn("failed", context.exception.cause.lower())

    @patch("requests.Session.post")
    def test_connection_test_unreachable_host_raises_exception(self, mock_post):
        """Test that an unreachable host raises ConnectionTestException."""
        connection = create_mock_connection()
        mock_post.side_effect = requests.exceptions.ConnectionError("Failed to establish a new connection")

        with self.assertRaises(ConnectionTestException):
            connection.test()

    @patch("requests.Session.post")
    def test_connection_test_ssl_validation_failure_raises_exception(self, mock_post):
        """Test that SSL validation failure raises ConnectionTestException."""
        connection = create_mock_connection()
        mock_post.side_effect = requests.exceptions.SSLError("SSL: CERTIFICATE_VERIFY_FAILED")

        with self.assertRaises(ConnectionTestException):
            connection.test()

    @patch("requests.Session.post")
    def test_session_expiry_and_reauthentication(self, mock_post):
        """Test that session expiry triggers re-authentication and retry."""
        connection = create_mock_session_connection()

        # Simulate: first call to login succeeds, then execute gets session expired,
        # then re-login succeeds, then retry succeeds
        success_response = {
            "id": 3,
            "result": [
                {
                    "status": {"code": 0, "message": "OK"},
                    "data": [{"name": "test-obj"}],
                }
            ],
        }

        mock_post.side_effect = [
            # Initial login (called by _execute_with_session since no session token)
            MockResponse(self.login_success_response),
            # First execute attempt returns session expired
            MockResponse(self.session_expired_response),
            # Re-authentication login
            MockResponse(self.login_success_response),
            # Retry execute succeeds
            MockResponse(success_response),
        ]

        # Use execute directly to test re-auth flow
        result = connection.api.execute("get", "/pm/config/adom/root/obj/firewall/address")

        # Should have called post 4 times: login, expired, re-login, success
        self.assertEqual(mock_post.call_count, 4)
        self.assertIsInstance(result, list)
