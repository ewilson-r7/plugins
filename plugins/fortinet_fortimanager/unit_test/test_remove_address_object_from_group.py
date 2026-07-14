import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch, MagicMock

from insightconnect_plugin_runtime.exceptions import PluginException

from icon_fortinet_fortimanager.actions.remove_address_object_from_group import RemoveAddressObjectFromGroup
from icon_fortinet_fortimanager.actions.remove_address_object_from_group.schema import Input, Output
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestRemoveAddressObjectFromGroup(TestCase):
    def setUp(self):
        self.action = RemoveAddressObjectFromGroup()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

    @patch("requests.Session.post")
    def test_remove_address_object_from_group_success(self, mock_post):
        """Test successfully removing an address object from a group."""
        get_group_response = load_payload("get_address_group.json.resp")
        update_group_response = load_payload("update_address_group.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
            MockResponse(update_group_response),
        ]

        params = {
            Input.ADDRESS_OBJECT: "google-dns",
            Input.GROUP: "blocked-addresses",
            Input.ADOM: "",
        }

        result = self.action.run(params)

        self.assertTrue(result[Output.SUCCESS])
        self.assertIn("cloudflare-dns", result[Output.ADDRESS_OBJECTS])
        self.assertNotIn("google-dns", result[Output.ADDRESS_OBJECTS])
        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 1)

    @patch("requests.Session.post")
    def test_remove_address_object_not_in_group(self, mock_post):
        """Test that PluginException is raised when address object is not in the group."""
        get_group_response = load_payload("get_address_group.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
        ]

        params = {
            Input.ADDRESS_OBJECT: "not-a-member",
            Input.GROUP: "blocked-addresses",
            Input.ADOM: "",
        }

        with self.assertRaises(PluginException) as context:
            self.action.run(params)

        self.assertIn("not a member", context.exception.cause)

    @patch("requests.Session.post")
    def test_remove_address_object_group_not_found(self, mock_post):
        """Test that PluginException is raised when the group does not exist."""
        error_response = load_payload("error_object_not_exist.json.resp")

        mock_post.side_effect = [
            MockResponse(error_response),
        ]

        params = {
            Input.ADDRESS_OBJECT: "bad-domain",
            Input.GROUP: "nonexistent-group",
            Input.ADOM: "",
        }

        with self.assertRaises(PluginException) as context:
            self.action.run(params)

        self.assertIn("code -3", context.exception.cause)

    @patch("requests.Session.post")
    def test_remove_address_object_with_adom_override(self, mock_post):
        """Test that the ADOM input overrides the connection default."""
        get_group_response = load_payload("get_address_group.json.resp")
        update_group_response = load_payload("update_address_group.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
            MockResponse(update_group_response),
        ]

        params = {
            Input.ADDRESS_OBJECT: "cloudflare-dns",
            Input.GROUP: "blocked-addresses",
            Input.ADOM: "custom-adom",
        }

        result = self.action.run(params)

        self.assertTrue(result[Output.SUCCESS])
        self.assertNotIn("cloudflare-dns", result[Output.ADDRESS_OBJECTS])
        self.assertIn("google-dns", result[Output.ADDRESS_OBJECTS])
        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 1)
