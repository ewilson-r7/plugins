import unittest
from unittest.mock import patch
from parameterized import parameterized
from insightconnect_plugin_runtime.exceptions import PluginException
from icon_halo_itsm.actions.update_ticket import UpdateTicket
from unit_test.util import default_connector, MockResponse, mock_auth_response


class TestUpdateTicket(unittest.TestCase):
    def setUp(self):
        with patch("requests.post", side_effect=mock_auth_response):
            self.action = default_connector(UpdateTicket())

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_update_ticket_success(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, "update_ticket_success.json")
        result = self.action.run({"ticket_id": 1234, "summary": "Email not working - UPDATED", "status_id": 3})
        self.assertIn("ticket", result)
        self.assertEqual(result["ticket"]["id"], 1234)
        self.assertEqual(result["ticket"]["summary"], "Email not working - UPDATED")
        self.assertEqual(result["ticket"]["status_id"], 3)

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_update_ticket_priority_only(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, "update_ticket_success.json")
        result = self.action.run({"ticket_id": 1234, "priority_id": 1})
        self.assertIn("ticket", result)

    @parameterized.expand(
        [
            ("not_found", 404),
            ("unauthorized", 401),
            ("bad_request", 400),
            ("server_error", 500),
        ]
    )
    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_update_ticket_error(self, _name, status_code, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({"ticket_id": 1234, "summary": "Test"})


if __name__ == "__main__":
    unittest.main()
