import unittest
from unittest.mock import patch
from parameterized import parameterized
from insightconnect_plugin_runtime.exceptions import PluginException
from icon_halo_itsm.actions.list_tickets import ListTickets
from unit_test.util import default_connector, MockResponse, mock_auth_response


class TestListTickets(unittest.TestCase):
    def setUp(self):
        with patch("requests.post", side_effect=mock_auth_response):
            self.action = default_connector(ListTickets())

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_list_tickets_success(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, "list_tickets_success.json")
        result = self.action.run({})
        self.assertIn("tickets", result)
        self.assertEqual(len(result["tickets"]), 2)
        self.assertEqual(result["tickets"][0]["id"], 1234)
        self.assertEqual(result["tickets"][1]["id"], 1235)

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_list_tickets_with_filters(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, "list_tickets_success.json")
        result = self.action.run({"status_id": 1, "count": 10, "search": "email"})
        self.assertIn("tickets", result)

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_list_tickets_empty(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, json_data={"tickets": []})
        result = self.action.run({})
        self.assertEqual(result["tickets"], [])

    @parameterized.expand(
        [
            ("unauthorized", 401),
            ("forbidden", 403),
            ("server_error", 500),
        ]
    )
    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_list_tickets_error(self, _name, status_code, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({})


if __name__ == "__main__":
    unittest.main()
