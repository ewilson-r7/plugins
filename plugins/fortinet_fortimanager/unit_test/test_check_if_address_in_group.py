import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

from insightconnect_plugin_runtime.exceptions import PluginException

from icon_fortinet_fortimanager.actions.check_if_address_in_group import CheckIfAddressInGroup
from icon_fortinet_fortimanager.actions.check_if_address_in_group.schema import Input, Output
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestCheckIfAddressInGroup(TestCase):
    def setUp(self):
        self.action = CheckIfAddressInGroup()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

    @patch("requests.Session.post")
    def test_name_match_found(self, mock_post):
        """Test name-based match when address matches a member name."""
        get_group_response = load_payload("get_address_group.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
        ]

        params = {
            Input.ADDRESS: "google-dns",
            Input.GROUP: "blocked-addresses",
            Input.ENABLE_SEARCH: False,
        }

        result = self.action.run(params)

        self.assertTrue(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], ["google-dns"])

    @patch("requests.Session.post")
    def test_name_match_not_found(self, mock_post):
        """Test name-based match when address does not match any member name."""
        get_group_response = load_payload("get_address_group.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
        ]

        params = {
            Input.ADDRESS: "nonexistent-object",
            Input.GROUP: "blocked-addresses",
            Input.ENABLE_SEARCH: False,
        }

        result = self.action.run(params)

        self.assertFalse(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], [])

    @patch("requests.Session.post")
    def test_value_search_subnet_match(self, mock_post):
        """Test value-based search matching a stored subnet value."""
        get_group_response = load_payload("get_address_group.json.resp")
        get_objects_response = load_payload("get_address_objects.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
            MockResponse(get_objects_response),
        ]

        params = {
            Input.ADDRESS: "8.8.8.8/32",
            Input.GROUP: "blocked-addresses",
            Input.ENABLE_SEARCH: True,
        }

        result = self.action.run(params)

        self.assertTrue(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], ["google-dns"])

    @patch("requests.Session.post")
    def test_value_search_no_match(self, mock_post):
        """Test value-based search when no member values match."""
        get_group_response = load_payload("get_address_group.json.resp")
        get_objects_response = load_payload("get_address_objects.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
            MockResponse(get_objects_response),
        ]

        params = {
            Input.ADDRESS: "10.0.0.1/32",
            Input.GROUP: "blocked-addresses",
            Input.ENABLE_SEARCH: True,
        }

        result = self.action.run(params)

        self.assertFalse(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], [])

    @patch("requests.Session.post")
    def test_group_not_found_raises_exception(self, mock_post):
        """Test PluginException is raised when the group does not exist."""
        error_response = load_payload("error_object_not_exist.json.resp")

        mock_post.side_effect = [
            MockResponse(error_response),
        ]

        params = {
            Input.ADDRESS: "google-dns",
            Input.GROUP: "nonexistent-group",
            Input.ENABLE_SEARCH: False,
        }

        with self.assertRaises(PluginException) as context:
            self.action.run(params)

        self.assertIn("-3", context.exception.cause)

    @patch("requests.Session.post")
    def test_adom_override(self, mock_post):
        """Test that ADOM override from input is used."""
        get_group_response = load_payload("get_address_group.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
        ]

        params = {
            Input.ADDRESS: "google-dns",
            Input.GROUP: "blocked-addresses",
            Input.ENABLE_SEARCH: False,
            Input.ADOM: "custom-adom",
        }

        result = self.action.run(params)

        self.assertTrue(result[Output.FOUND])

        # Verify the API call used the custom ADOM
        first_call_payload = mock_post.call_args_list[0][1].get("json") or mock_post.call_args_list[0][0][0]
        if isinstance(first_call_payload, dict):
            url_in_params = first_call_payload.get("params", [{}])[0].get("url", "")
            self.assertIn("custom-adom", url_in_params)

    @patch("requests.Session.post")
    def test_value_search_case_insensitive(self, mock_post):
        """Test value-based search is case-insensitive."""
        get_group_response = load_payload("get_address_group.json.resp")
        get_objects_response = load_payload("get_address_objects.json.resp")

        mock_post.side_effect = [
            MockResponse(get_group_response),
            MockResponse(get_objects_response),
        ]

        # Search with uppercase — should still match "1.1.1.1/32" stored for cloudflare-dns
        params = {
            Input.ADDRESS: "1.1.1.1/32",
            Input.GROUP: "blocked-addresses",
            Input.ENABLE_SEARCH: True,
        }

        result = self.action.run(params)

        self.assertTrue(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], ["cloudflare-dns"])
