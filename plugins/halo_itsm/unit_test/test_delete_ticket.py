import unittest
from unittest.mock import patch
from parameterized import parameterized
from insightconnect_plugin_runtime.exceptions import PluginException
from icon_halo_itsm.actions.delete_ticket import DeleteTicket
from unit_test.util import default_connector, MockResponse, mock_auth_response


class TestDeleteTicket(unittest.TestCase):
    def setUp(self):
        with patch("requests.post", side_effect=mock_auth_response):
            self.action = default_connector(DeleteTicket())

    @patch("requests.Session.request")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_delete_ticket_success(self, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(204)
        result = self.action.run({"ticket_id": 1234})
        self.assertTrue(result["success"])

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
    def test_delete_ticket_error(self, _name, status_code, _mock_auth, mock_request):
        mock_request.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run({"ticket_id": 9999})


if __name__ == "__main__":
    unittest.main()
