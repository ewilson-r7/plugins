import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

from insightconnect_plugin_runtime.exceptions import PluginException

from icon_fortinet_fortimanager.actions.check_if_address_in_group import CheckIfAddressInGroup
from icon_fortinet_fortimanager.actions.check_if_address_in_group.schema import (
    CheckIfAddressInGroupOutput,
    Input,
    Output,
)
from jsonschema import validate
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestCheckIfAddressInGroup(TestCase):
    def setUp(self):
        self.action = CheckIfAddressInGroup()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger
        self.group_response = load_payload("get_address_group.json.resp")
        self.objects_response = load_payload("get_address_objects.json.resp")

    def _mock_calls(self, mock_post):
        """Group lookup followed by the address object lookup used for value matching."""
        mock_post.side_effect = [
            MockResponse(self.group_response),
            MockResponse(self.objects_response),
        ]

    @patch("requests.post")
    def test_match_by_object_name(self, mock_post):
        """An address input that is a member object name is matched by name."""
        self._mock_calls(mock_post)

        result = self.action.run({Input.ADDRESS: "google-dns", Input.GROUP: "blocked-addresses"})

        self.assertTrue(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], ["google-dns"])
        self.assertIn("google-dns", result[Output.MESSAGE])
        validate(result, CheckIfAddressInGroupOutput.schema)

    @patch("requests.post")
    def test_match_by_object_name_is_case_insensitive(self, mock_post):
        """Name matching ignores case."""
        self._mock_calls(mock_post)

        result = self.action.run({Input.ADDRESS: "GOOGLE-DNS", Input.GROUP: "blocked-addresses"})

        self.assertTrue(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], ["google-dns"])

    @patch("requests.post")
    def test_match_by_cidr_against_netmask_subnet(self, mock_post):
        """A CIDR input matches FortiManager's address-plus-netmask list form.

        This is the case that crashed in 2.1.0 with "'list' object has no attribute
        'lower'" because the stored subnet arrives as ["8.8.8.8", "255.255.255.255"].
        """
        self._mock_calls(mock_post)

        result = self.action.run({Input.ADDRESS: "8.8.8.8/32", Input.GROUP: "blocked-addresses"})

        self.assertTrue(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], ["google-dns"])
        validate(result, CheckIfAddressInGroupOutput.schema)

    @patch("requests.post")
    def test_match_by_bare_ip_against_netmask_subnet(self, mock_post):
        """A bare IP matches a /32 object without the caller supplying a prefix."""
        self._mock_calls(mock_post)

        result = self.action.run({Input.ADDRESS: "1.1.1.1", Input.GROUP: "blocked-addresses"})

        self.assertTrue(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], ["cloudflare-dns"])

    @patch("requests.post")
    def test_no_match_returns_found_false(self, mock_post):
        """An address that is neither a member name nor a member value is not found."""
        self._mock_calls(mock_post)

        result = self.action.run({Input.ADDRESS: "10.0.0.1/32", Input.GROUP: "blocked-addresses"})

        self.assertFalse(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], [])
        self.assertIn("No address object matching", result[Output.MESSAGE])
        validate(result, CheckIfAddressInGroupOutput.schema)

    @patch("requests.post")
    def test_non_member_object_value_is_not_matched(self, mock_post):
        """Only objects that belong to the group are considered.

        internal-net exists in the ADOM but is not a member of the group, so its
        subnet must not produce a match.
        """
        self._mock_calls(mock_post)

        result = self.action.run({Input.ADDRESS: "192.168.1.0/24", Input.GROUP: "blocked-addresses"})

        self.assertFalse(result[Output.FOUND])
        self.assertEqual(result[Output.ADDRESS_OBJECTS], [])

    @patch("requests.post")
    def test_group_not_found_raises_exception(self, mock_post):
        """A missing group is a genuine failure and still raises."""
        mock_post.side_effect = [MockResponse(load_payload("error_object_not_exist.json.resp"))]

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.ADDRESS: "google-dns", Input.GROUP: "nonexistent-group"})

        self.assertIn("-3", context.exception.cause)

    @patch("requests.post")
    def test_adom_override(self, mock_post):
        """The ADOM input overrides the connection default."""
        self._mock_calls(mock_post)

        result = self.action.run(
            {
                Input.ADDRESS: "google-dns",
                Input.GROUP: "blocked-addresses",
                Input.ADOM: "custom-adom",
            }
        )

        self.assertTrue(result[Output.FOUND])
        first_call = mock_post.call_args_list[0][1].get("json") or mock_post.call_args_list[0][0][0]
        self.assertIn("custom-adom", first_call.get("params", [{}])[0].get("url", ""))
