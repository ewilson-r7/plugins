"""Unit tests for GetTicket action."""

import unittest
from unittest.mock import patch

from insightconnect_plugin_runtime.exceptions import PluginException
from parameterized import parameterized

from icon_teamdynamix.actions.get_ticket import GetTicket
from unit_test.util import default_connector, MockResponse, AUTH_TOKEN


class TestGetTicket(unittest.TestCase):
    def setUp(self):
        self.action = default_connector(GetTicket())
        self.action.connection.client._token = AUTH_TOKEN

    # ------------------------------------------------------------------
    # Happy-path tests
    # ------------------------------------------------------------------

    @patch("requests.Session.request")
    def test_get_ticket_success(self, mock_request):
        mock_request.return_value = MockResponse(200, "get_ticket_success.json")
        result = self.action.run({"ticket_id": 12345})

        self.assertEqual(result["ticket_id"], 12345)
        self.assertEqual(result["title"], "Remediate Critical Vulnerability CVE-2024-1234")
        self.assertEqual(result["status"], "New")
        self.assertIsInstance(result["ticket"], dict)
        self.assertEqual(result["ticket"]["ID"], 12345)

    @parameterized.expand(
        [
            ("by_id_100", {"ticket_id": 100}),
            ("by_id_999", {"ticket_id": 999}),
        ]
    )
    @patch("requests.Session.request")
    def test_get_ticket_various_ids(self, _name, input_params, mock_request):
        mock_request.return_value = MockResponse(200, "get_ticket_success.json")
        result = self.action.run(input_params)
        self.assertIn("ticket", result)

    # ------------------------------------------------------------------
    # Error-path tests
    # ------------------------------------------------------------------

    @parameterized.expand(
        [
            ("not_found", 404),
            ("unauthorized", 401),
            ("forbidden", 403),
            ("bad_request", 400),
            ("server_error", 500),
        ]
    )
    @patch("requests.Session.request")
    def test_get_ticket_http_error(self, _name, status_code, mock_request):
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({"ticket_id": 12345})

    @patch("requests.Session.request")
    def test_get_ticket_empty_response_raises(self, mock_request):
        """Empty dict response (e.g. 204-like) should raise PluginException."""
        mock_request.return_value = MockResponse(204)
        # make_request returns {} on 204, then GetTicket raises on falsy response
        with self.assertRaises(PluginException):
            self.action.run({"ticket_id": 12345})
