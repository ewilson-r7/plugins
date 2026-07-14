import unittest
from unittest.mock import patch
from parameterized import parameterized
from insightconnect_plugin_runtime.exceptions import PluginException
from icon_halo_itsm.actions.attach_file_to_ticket import AttachFileToTicket
from unit_test.util import default_connector, MockResponse, mock_auth_response


class TestAttachFileToTicket(unittest.TestCase):
    def setUp(self):
        with patch("requests.post", side_effect=mock_auth_response):
            self.action = default_connector(AttachFileToTicket())

    @patch("requests.Session.post")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_attach_file_success(self, _mock_auth, mock_post):
        mock_post.return_value = MockResponse(200, "attach_file_success.json")
        result = self.action.run(
            {
                "ticket_id": 1234,
                "filename": "error_log.txt",
                "content": "VGhpcyBpcyBhIHRlc3QgZmlsZQ==",
                "note": "Attaching error log for reference",
                "hiddenfromuser": False,
            }
        )
        self.assertIn("action", result)
        self.assertEqual(result["action"]["id"], 502)
        self.assertEqual(result["action"]["ticket_id"], 1234)
        self.assertEqual(result["action"]["note"], "Attaching error log for reference")

    @patch("requests.Session.post")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_attach_file_without_note(self, _mock_auth, mock_post):
        mock_post.return_value = MockResponse(200, "attach_file_success.json")
        result = self.action.run(
            {
                "ticket_id": 1234,
                "filename": "screenshot.png",
                "content": "iVBORw0KGgoAAAANSUhEUg==",
            }
        )
        self.assertIn("action", result)

    @patch("requests.Session.post")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_attach_file_invalid_base64(self, _mock_auth, mock_post):
        # Invalid base64 should raise PluginException
        with self.assertRaises(PluginException):
            self.action.run(
                {
                    "ticket_id": 1234,
                    "filename": "bad.txt",
                    "content": "!!!not-valid-base64!!!",
                }
            )

    @parameterized.expand(
        [
            ("not_found", 404),
            ("unauthorized", 401),
            ("bad_request", 400),
            ("server_error", 500),
        ]
    )
    @patch("requests.Session.post")
    @patch("requests.post", side_effect=mock_auth_response)
    def test_attach_file_error(self, _name, status_code, _mock_auth, mock_post):
        mock_post.return_value = MockResponse(status_code)
        with self.assertRaises(PluginException):
            self.action.run(
                {
                    "ticket_id": 9999,
                    "filename": "test.txt",
                    "content": "VGVzdA==",
                }
            )


if __name__ == "__main__":
    unittest.main()
