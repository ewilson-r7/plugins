"""Unit tests for UpdateTicket action."""

import unittest
from unittest.mock import patch, MagicMock

from insightconnect_plugin_runtime.exceptions import PluginException
from parameterized import parameterized

from icon_teamdynamix.actions.update_ticket import UpdateTicket
from unit_test.util import default_connector, MockResponse, AUTH_TOKEN


class TestUpdateTicket(unittest.TestCase):
    def setUp(self):
        self.action = default_connector(UpdateTicket())
        self.action.connection.client._token = AUTH_TOKEN

    # ------------------------------------------------------------------
    # Happy-path tests
    # ------------------------------------------------------------------

    @patch("requests.Session.request")
    def test_update_ticket_success_title_only(self, mock_request):
        # First call: GET current ticket; second call: POST update
        mock_request.side_effect = [
            MockResponse(200, "get_ticket_success.json"),
            MockResponse(200, "get_ticket_success.json"),
        ]
        result = self.action.run({"ticket_id": 12345, "title": "Updated Title"})
        self.assertTrue(result["success"])

    @parameterized.expand(
        [
            (
                "update_status_and_priority",
                {"ticket_id": 12345, "status_id": 602, "priority_id": 20},
            ),
            (
                "update_description",
                {"ticket_id": 12345, "description": "New description text"},
            ),
            (
                "update_with_additional_fields",
                {"ticket_id": 12345, "additional_fields": {"CustomAttr": "val"}},
            ),
        ]
    )
    @patch("requests.Session.request")
    def test_update_ticket_variants(self, _name, input_params, mock_request):
        mock_request.side_effect = [
            MockResponse(200, "get_ticket_success.json"),
            MockResponse(200, "get_ticket_success.json"),
        ]
        result = self.action.run(input_params)
        self.assertTrue(result["success"])

    @patch("requests.Session.request")
    def test_update_ticket_post_returns_204(self, mock_request):
        """POST returning 204 (no content) is also a success."""
        mock_request.side_effect = [
            MockResponse(200, "get_ticket_success.json"),
            MockResponse(204),
        ]
        result = self.action.run({"ticket_id": 12345, "status_id": 602})
        self.assertTrue(result["success"])

    # ------------------------------------------------------------------
    # Error-path tests
    # ------------------------------------------------------------------

    @parameterized.expand(
        [
            ("not_found_on_get", 404),
            ("unauthorized_on_get", 401),
            ("server_error_on_get", 500),
        ]
    )
    @patch("requests.Session.request")
    def test_update_ticket_get_error(self, _name, status_code, mock_request):
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({"ticket_id": 12345, "title": "New Title"})

    @patch("requests.Session.request")
    def test_update_ticket_post_error(self, mock_request):
        """GET succeeds but POST returns an error."""
        mock_request.side_effect = [
            MockResponse(200, "get_ticket_success.json"),
            MockResponse(500),
        ]
        with self.assertRaises(PluginException):
            self.action.run({"ticket_id": 12345, "title": "New Title"})
