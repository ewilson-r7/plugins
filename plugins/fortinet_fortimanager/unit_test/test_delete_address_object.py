import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch, MagicMock

from icon_fortinet_fortimanager.actions.delete_address_object import DeleteAddressObject
from icon_fortinet_fortimanager.actions.delete_address_object.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestDeleteAddressObject(TestCase):
    def setUp(self):
        self.action = DeleteAddressObject()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

        # Load payloads for mocking
        self.mock_success_response = load_payload("delete_address_object.json.resp")
        self.mock_error_not_found = load_payload("error_object_not_exist.json.resp")

    @patch("requests.Session.post")
    def test_delete_address_object_success(self, mock_post):
        """Test successful deletion of an address object."""
        mock_post.return_value = MockResponse(self.mock_success_response)

        result = self.action.run({Input.ADDRESS_OBJECT: "malicious-host"})

        self.assertTrue(result[Output.SUCCESS])
        mock_post.assert_called_once()

    @patch("requests.Session.post")
    def test_delete_object_not_found_raises_plugin_exception(self, mock_post):
        """Test that deleting a non-existent object raises PluginException."""
        mock_post.return_value = MockResponse(self.mock_error_not_found)

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.ADDRESS_OBJECT: "nonexistent-object"})

        self.assertIn("-3", context.exception.cause)

    @patch("requests.Session.post")
    def test_delete_object_in_use_raises_plugin_exception(self, mock_post):
        """Test that deleting an object referenced by a group/policy raises PluginException."""
        # Simulate a "referenced object" error — FortiManager returns a specific error
        # when trying to delete an object that is in use by a group or policy.
        # This is typically error code -10015 or a variant with a descriptive message.
        error_in_use_response = {
            "id": 1,
            "result": [
                {
                    "status": {
                        "code": -10015,
                        "message": "The object is being used by other objects and cannot be deleted",
                    }
                }
            ],
        }
        mock_post.return_value = MockResponse(error_in_use_response)

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.ADDRESS_OBJECT: "used-object"})

        self.assertIn("-10015", context.exception.cause)

    @patch("requests.Session.post")
    def test_delete_address_object_with_adom_override(self, mock_post):
        """Test that ADOM input overrides connection default."""
        mock_post.return_value = MockResponse(self.mock_success_response)

        result = self.action.run(
            {
                Input.ADDRESS_OBJECT: "malicious-host",
                Input.ADOM: "custom-adom",
            }
        )

        self.assertTrue(result[Output.SUCCESS])
        mock_post.assert_called_once()
        # Verify the request uses the custom ADOM
        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][0]
        request_url = payload["params"][0]["url"]
        self.assertIn("custom-adom", request_url)
