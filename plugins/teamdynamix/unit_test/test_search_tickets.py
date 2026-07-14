"""Unit tests for SearchTickets action."""

import unittest
from unittest.mock import patch

from insightconnect_plugin_runtime.exceptions import PluginException
from parameterized import parameterized

from icon_teamdynamix.actions.search_tickets import SearchTickets
from unit_test.util import default_connector, MockResponse, AUTH_TOKEN


class TestSearchTickets(unittest.TestCase):
    def setUp(self):
        self.action = default_connector(SearchTickets())
        self.action.connection.client._token = AUTH_TOKEN

    # ------------------------------------------------------------------
    # Happy-path tests
    # ------------------------------------------------------------------

    @patch("requests.Session.request")
    def test_search_tickets_returns_results(self, mock_request):
        mock_request.return_value = MockResponse(200, "search_tickets_success.json")
        result = self.action.run({"search_text": "CVE-2024", "max_results": 25})

        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["tickets"]), 2)
        self.assertEqual(result["tickets"][0]["ID"], 12345)

    @patch("requests.Session.request")
    def test_search_tickets_empty_result(self, mock_request):
        mock_request.return_value = MockResponse(200, "search_tickets_empty.json")
        result = self.action.run({"max_results": 25})

        self.assertEqual(result["count"], 0)
        self.assertEqual(result["tickets"], [])

    @parameterized.expand(
        [
            ("with_search_text_only", {"search_text": "CVE", "max_results": 10}),
            ("with_status_filter", {"status_id": 602, "max_results": 5}),
            ("with_all_filters", {"search_text": "CVE", "status_id": 602, "max_results": 50}),
            ("no_filters", {"max_results": 25}),
        ]
    )
    @patch("requests.Session.request")
    def test_search_tickets_filter_variants(self, _name, input_params, mock_request):
        mock_request.return_value = MockResponse(200, "search_tickets_success.json")
        result = self.action.run(input_params)
        self.assertIn("tickets", result)
        self.assertIn("count", result)

    @patch("requests.Session.request")
    def test_search_tickets_non_list_response_returns_empty(self, mock_request):
        """If the API returns a non-list (e.g. an object), tickets defaults to []."""
        mock_request.return_value = MockResponse(200, text='{"error": "unexpected"}')
        result = self.action.run({"max_results": 25})
        self.assertEqual(result["tickets"], [])
        self.assertEqual(result["count"], 0)

    # ------------------------------------------------------------------
    # Error-path tests
    # ------------------------------------------------------------------

    @parameterized.expand(
        [
            ("unauthorized", 401),
            ("forbidden", 403),
            ("bad_request", 400),
            ("server_error", 500),
            ("service_unavailable", 503),
        ]
    )
    @patch("requests.Session.request")
    def test_search_tickets_http_error(self, _name, status_code, mock_request):
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({"max_results": 25})
