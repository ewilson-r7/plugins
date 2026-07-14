import unittest
from unittest.mock import patch
from parameterized import parameterized
from insightconnect_plugin_runtime.exceptions import PluginException
from icon_halo_itsm.actions.add_action_to_ticket import AddActionToTicket
from unit_test.util import default_connector, MockResponse, mock_auth_response


class TestAddActionToTicket(unittest.TestCase):
    def setUp(self):
        with patch("requests.post", side_effect=mock_auth_response):
            self.action = default_connector(AddActionToTicket())

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_add_action_success(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, "add_action_success.json")
        result = self.action.run(
            {
                "ticket_id": 1234,
                "note": "Investigated the issue and found root cause",
                "outcome": "Ongoing",
                "hiddenfromuser": False,
            }
        )
        self.assertIn("action", result)
        self.assertEqual(result["action"]["id"], 501)
        self.assertEqual(result["action"]["ticket_id"], 1234)
        self.assertEqual(result["action"]["note"], "Investigated the issue and found root cause")

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_add_action_hidden_note(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(200, "add_action_success.json")
        result = self.action.run(
            {
                "ticket_id": 1234,
                "note": "Internal note",
                "hiddenfromuser": True,
            }
        )
        self.assertIn("action", result)

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
    def test_add_action_error(self, _name, status_code, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({"ticket_id": 9999, "note": "Test note"})


if __name__ == "__main__":
    unittest.main()
