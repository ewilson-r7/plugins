import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch, MagicMock

from icon_fortinet_fortimanager.actions.delete_address_object import DeleteAddressObject
from icon_fortinet_fortimanager.actions.delete_address_object.schema import (
    DeleteAddressObjectOutput,
    Input,
    Output,
)
from insightconnect_plugin_runtime.exceptions import PluginException
from jsonschema import validate
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestDeleteAddressObject(TestCase):
    def setUp(self):
        self.action = DeleteAddressObject()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

        # Load payloads for mocking
        self.mock_success_response = load_payload("delete_address_object.json.resp")
        self.mock_error_not_found = load_payload("error_object_not_exist.json.resp")

    @patch("requests.post")
    def test_delete_address_object_success(self, mock_post):
        """Test successful deletion of an address object."""
        mock_post.return_value = MockResponse(self.mock_success_response)

        result = self.action.run({Input.ADDRESS_OBJECT: "malicious-host"})

        self.assertTrue(result[Output.SUCCESS])
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_delete_object_not_found_returns_false(self, mock_post):
        """Test that deleting a non-existent object returns success=False gracefully."""
        mock_post.return_value = MockResponse(self.mock_error_not_found)

        result = self.action.run({Input.ADDRESS_OBJECT: "nonexistent-object"})

        self.assertFalse(result[Output.SUCCESS])

    @patch("requests.post")
    def test_delete_object_in_use_reports_reason(self, mock_post):
        """An object still referenced by a group or policy is reported, not raised.

        FortiManager returns code -10015 with the message 'used', so the code is what
        the action matches on. In 2.1.0 this raised and failed the workflow step.
        """
        error_in_use_response = {
            "id": 1,
            "result": [
                {
                    "status": {
                        "code": -10015,
                        "message": "used",
                    }
                }
            ],
        }
        mock_post.return_value = MockResponse(error_in_use_response)

        result = self.action.run({Input.ADDRESS_OBJECT: "used-object"})

        self.assertFalse(result[Output.SUCCESS])
        self.assertIn("still in use", result[Output.MESSAGE])
        validate(result, DeleteAddressObjectOutput.schema)

    @patch("requests.post")
    def test_delete_object_in_use_reported_by_message_alone(self, mock_post):
        """The in-use condition is recognized from the message even under a different code.

        FortiManager's status code for this varies by version, so the message is a
        fallback for when the code is not the documented -10015.
        """
        mock_post.return_value = MockResponse(
            {"id": 1, "result": [{"status": {"code": -2, "message": "object is in use by addrgrp"}}]}
        )

        result = self.action.run({Input.ADDRESS_OBJECT: "used-object"})

        self.assertFalse(result[Output.SUCCESS])
        self.assertIn("still in use", result[Output.MESSAGE])
        validate(result, DeleteAddressObjectOutput.schema)

    @patch("requests.post")
    def test_unrelated_error_still_raises(self, mock_post):
        """An error that is neither absent nor in-use is a genuine failure."""
        mock_post.return_value = MockResponse(
            {"id": 1, "result": [{"status": {"code": -1, "message": "No permission for the resource"}}]}
        )

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.ADDRESS_OBJECT: "some-object"})

        self.assertIn("No permission", context.exception.cause)

    @patch("requests.post")
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
