import unittest
from unittest.mock import patch
from parameterized import parameterized
from insightconnect_plugin_runtime.exceptions import PluginException
from icon_halo_itsm.actions.create_ticket import CreateTicket
from unit_test.util import default_connector, MockResponse, mock_auth_response


class TestCreateTicket(unittest.TestCase):
    def setUp(self):
        with patch("requests.post", side_effect=mock_auth_response):
            self.action = default_connector(CreateTicket())

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_create_ticket_success(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, "create_ticket_success.json")
        result = self.action.run({"summary": "Server is unresponsive", "tickettype_id": 1})
        self.assertIn("ticket", result)
        self.assertEqual(result["ticket"]["id"], 101)
        self.assertEqual(result["ticket"]["summary"], "Server is unresponsive")

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_create_ticket_with_optional_fields(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, "create_ticket_success.json")
        result = self.action.run(
            {
                "summary": "Server is unresponsive",
                "tickettype_id": 1,
                "priority_id": 3,
                "agent_id": 15,
                "category_1": "Hardware",
            }
        )
        self.assertIn("ticket", result)
        self.assertEqual(result["ticket"]["id"], 101)

    @parameterized.expand(
        [
            ("bad_request", 400),
            ("unauthorized", 401),
            ("forbidden", 403),
            ("server_error", 500),
        ]
    )
    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_create_ticket_error(self, _name, status_code, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({"summary": "Test", "tickettype_id": 1})


if __name__ == "__main__":
    unittest.main()
