import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch, MagicMock

from insightconnect_plugin_runtime.exceptions import PluginException

from icon_fortinet_fortimanager.actions.add_address_object_to_group import AddAddressObjectToGroup
from icon_fortinet_fortimanager.actions.add_address_object_to_group.schema import (
    AddAddressObjectToGroupOutput,
    Input,
    Output,
)
from jsonschema import validate
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestAddAddressObjectToGroup(TestCase):
    def setUp(self):
        self.action = AddAddressObjectToGroup()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

    @patch("requests.post")
    def test_add_address_object_to_group_success(self, mock_post):
        """Test successfully adding a new address object to a group."""
        # First call: get_address_group returns existing group
        # Second call: update_address_group succeeds
        get_group_response = load_payload("get_address_group.json.resp")
        update_group_response = load_payload("update_address_group.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
            MockResponse(update_group_response),
        ]

        params = {
            Input.ADDRESS_OBJECT: "example-fqdn",
            Input.GROUP: "blocked-addresses",
        }

        result = self.action.run(params)

        self.assertTrue(result[Output.SUCCESS])
        self.assertIn("example-fqdn", result[Output.ADDRESS_OBJECTS])
        self.assertIn("google-dns", result[Output.ADDRESS_OBJECTS])
        self.assertIn("cloudflare-dns", result[Output.ADDRESS_OBJECTS])
        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 3)

    @patch("requests.post")
    def test_add_address_object_to_group_idempotent(self, mock_post):
        """Test that adding an object already in the group returns current list without duplicate."""
        get_group_response = load_payload("get_address_group.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
        ]

        params = {
            Input.ADDRESS_OBJECT: "google-dns",
            Input.GROUP: "blocked-addresses",
        }

        result = self.action.run(params)

        self.assertTrue(result[Output.SUCCESS])
        self.assertIn("google-dns", result[Output.ADDRESS_OBJECTS])
        # Should NOT have duplicated google-dns
        self.assertEqual(result[Output.ADDRESS_OBJECTS].count("google-dns"), 1)
        # update_address_group should NOT have been called (only 1 mock call consumed)
        self.assertEqual(mock_post.call_count, 1)

    @patch("requests.post")
    def test_add_address_object_to_group_not_found(self, mock_post):
        """Test that PluginException is raised when group does not exist."""
        error_response = load_payload("error_object_not_exist.json.resp")

        mock_post.side_effect = [
            MockResponse(error_response),
        ]

        params = {
            Input.ADDRESS_OBJECT: "example-fqdn",
            Input.GROUP: "nonexistent-group",
        }

        with self.assertRaises(PluginException) as context:
            self.action.run(params)

        self.assertIn("-3", context.exception.cause)

    @patch("requests.post")
    def test_add_address_object_to_group_with_adom_override(self, mock_post):
        """Test ADOM override from action input."""
        get_group_response = load_payload("get_address_group.json.resp")
        update_group_response = load_payload("update_address_group.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
            MockResponse(update_group_response),
        ]

        params = {
            Input.ADDRESS_OBJECT: "new-object",
            Input.GROUP: "blocked-addresses",
            Input.ADOM: "custom-adom",
        }

        result = self.action.run(params)

        self.assertTrue(result[Output.SUCCESS])
        self.assertIn("new-object", result[Output.ADDRESS_OBJECTS])

        # Verify the API call used the custom ADOM
        first_call_payload = mock_post.call_args_list[0][1].get("json") or mock_post.call_args_list[0][0][0]
        # The URL in the payload should contain "custom-adom"
        if isinstance(first_call_payload, dict):
            url_in_params = first_call_payload.get("params", [{}])[0].get("url", "")
            self.assertIn("custom-adom", url_in_params)

    @patch("requests.post")
    def test_missing_address_object_raises_actionable_error(self, mock_post):
        """A member that does not exist yields a clear error, not the raw datasrc message.

        This is the response from the customer tenant. FortiManager rejects the update
        with code -10131 and the message "datasrc invalid ... solution: data not exist".
        The requested end state cannot be reached, so this stays a failure rather than
        being reported through the output - a block list that never received the address
        must not look like a success.
        """
        mock_post.side_effect = [
            MockResponse(load_payload("get_address_group.json.resp")),
            MockResponse(load_payload("error_datasrc_invalid.json.resp")),
        ]

        with self.assertRaises(PluginException) as context:
            self.action.run(
                {
                    Input.ADDRESS_OBJECT: "TEST_ADDR-8.2.15.5_32",
                    Input.GROUP: "TESTGROUP",
                }
            )

        cause = context.exception.cause
        self.assertIn("TEST_ADDR-8.2.15.5_32", cause)
        self.assertIn("does not exist", cause)
        self.assertIn("TESTGROUP", cause)
        # The raw API wording must not be what the analyst sees
        self.assertNotIn("datasrc", cause)
        self.assertIn("Create Address Object", context.exception.assistance)

    @patch("requests.post")
    def test_success_returns_message(self, mock_post):
        """The added path reports what happened."""
        mock_post.side_effect = [
            MockResponse(load_payload("get_address_group.json.resp")),
            MockResponse(load_payload("update_address_group.json.resp")),
        ]

        result = self.action.run({Input.ADDRESS_OBJECT: "example-fqdn", Input.GROUP: "blocked-addresses"})

        self.assertIn("added to group", result[Output.MESSAGE])
        self.assertIn("3 members total", result[Output.MESSAGE])
        validate(result, AddAddressObjectToGroupOutput.schema)

    @patch("requests.post")
    def test_already_a_member_returns_message(self, mock_post):
        """The idempotent path explains that nothing changed."""
        mock_post.side_effect = [MockResponse(load_payload("get_address_group.json.resp"))]

        result = self.action.run({Input.ADDRESS_OBJECT: "google-dns", Input.GROUP: "blocked-addresses"})

        self.assertTrue(result[Output.SUCCESS])
        self.assertIn("already a member", result[Output.MESSAGE])
        validate(result, AddAddressObjectToGroupOutput.schema)

    @patch("requests.post")
    def test_add_address_object_to_group_update_fails(self, mock_post):
        """Test PluginException raised when update fails (e.g., address object doesn't exist)."""
        get_group_response = load_payload("get_address_group.json.resp")
        error_response = load_payload("error_object_not_exist.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
            MockResponse(error_response),
        ]

        params = {
            Input.ADDRESS_OBJECT: "nonexistent-object",
            Input.GROUP: "blocked-addresses",
        }

        with self.assertRaises(PluginException) as context:
            self.action.run(params)

        self.assertIn("-3", context.exception.cause)
