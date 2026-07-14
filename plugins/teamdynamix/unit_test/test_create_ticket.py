"""Unit tests for CreateTicket action."""

import unittest
from unittest.mock import patch, call

from insightconnect_plugin_runtime.exceptions import PluginException
from parameterized import parameterized

from icon_teamdynamix.actions.create_ticket import CreateTicket
from unit_test.util import default_connector, MockResponse, AUTH_TOKEN


class TestCreateTicket(unittest.TestCase):
    def setUp(self):
        self.action = default_connector(CreateTicket())
        # Pre-seed a token so _authenticate is not triggered during most tests
        self.action.connection.client._token = AUTH_TOKEN

    # ------------------------------------------------------------------
    # Happy-path tests
    # ------------------------------------------------------------------

    @parameterized.expand(
        [
            (
                "with_required_fields_only",
                {"title": "Remediate CVE-2024-1234", "type_id": 123},
            ),
            (
                "with_all_optional_fields",
                {
                    "title": "Remediate CVE-2024-1234",
                    "type_id": 123,
                    "description": "Details here",
                    "form_id": 456,
                    "account_id": 789,
                    "priority_id": 20,
                    "requestor_uid": "aaaa-bbbb",
                    "responsible_group_id": 100,
                    "additional_fields": {"CustomAttr": "value"},
                },
            ),
        ]
    )
    @patch("requests.Session.request")
    def test_create_ticket_success(self, _name, input_params, mock_request):
        mock_request.return_value = MockResponse(200, "create_ticket_success.json")
        result = self.action.run(input_params)

        self.assertEqual(result["ticket_id"], 12345)
        self.assertIn("12345", result["ticket_url"])
        self.assertTrue(result["success"])

    # ------------------------------------------------------------------
    # Error-path tests
    # ------------------------------------------------------------------

    @parameterized.expand(
        [
            ("bad_request", 400),
            ("unauthorized", 401),
            ("forbidden", 403),
            ("not_found", 404),
            ("server_error", 500),
            ("service_unavailable", 503),
        ]
    )
    @patch("requests.Session.request")
    def test_create_ticket_http_error(self, _name, status_code, mock_request):
        # First call returns the error status; re-auth path returns a new token on 401
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({"title": "Test", "type_id": 1})

    @patch("requests.Session.request")
    def test_create_ticket_missing_id_in_response(self, mock_request):
        """API returns 200 but no ID field — should raise PluginException."""
        mock_request.return_value = MockResponse(200, text='{"Title": "No ID here"}')
        with self.assertRaises(PluginException):
            self.action.run({"title": "Test", "type_id": 1})

    @patch("requests.Session.request")
    def test_create_ticket_non_json_response(self, mock_request):
        mock_request.return_value = MockResponse(200, text="not-json")
        with self.assertRaises(PluginException):
            self.action.run({"title": "Test", "type_id": 1})
