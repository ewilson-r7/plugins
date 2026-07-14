import unittest
from unittest.mock import patch
from parameterized import parameterized
from insightconnect_plugin_runtime.exceptions import PluginException
from icon_halo_itsm.actions.get_ticket import GetTicket
from unit_test.util import default_connector, MockResponse, mock_auth_response


class TestGetTicket(unittest.TestCase):
    def setUp(self):
        with patch("requests.post", side_effect=mock_auth_response):
            self.action = default_connector(GetTicket())

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_get_ticket_success(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, "get_ticket_success.json")
        result = self.action.run({"ticket_id": 1234})
        self.assertIn("ticket", result)
        self.assertEqual(result["ticket"]["id"], 1234)
        self.assertEqual(result["ticket"]["summary"], "Email not working")
        self.assertEqual(result["ticket"]["agent_name"], "John Smith")

    @parameterized.expand(
        [
            ("not_found", 404),
            ("unauthorized", 401),
            ("forbidden", 403),
            ("server_error", 500),
        ]
    )
    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_get_ticket_error(self, _name, status_code, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({"ticket_id": 9999})


if __name__ == "__main__":
    unittest.main()
