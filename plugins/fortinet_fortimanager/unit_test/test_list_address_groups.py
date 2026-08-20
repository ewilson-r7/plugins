import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

from jsonschema import validate

from icon_fortinet_fortimanager.actions.list_address_groups import ListAddressGroups
from icon_fortinet_fortimanager.actions.list_address_groups.schema import ListAddressGroupsOutput, Input, Output
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestListAddressGroups(TestCase):
    def setUp(self):
        self.action = ListAddressGroups()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

    def _run_against_fixture(self, mock_post):
        mock_post.return_value = MockResponse(load_payload("get_address_groups.json.resp"))
        result = self.action.run({})
        return result, {group["name"]: group for group in result[Output.ADDRESS_GROUPS]}

    @patch("requests.post")
    def test_list_address_groups_returns_all(self, mock_post):
        """All groups in the ADOM are returned and the output is schema valid."""
        result, by_name = self._run_against_fixture(mock_post)

        self.assertEqual(len(result[Output.ADDRESS_GROUPS]), 4)
        self.assertEqual(result[Output.ADDRESS_GROUPS][0]["name"], "blocked-addresses")
        self.assertIn("4 address groups", result[Output.MESSAGE])
        validate(result, ListAddressGroupsOutput.schema)

    @patch("requests.post")
    def test_members_returned_as_objects_are_flattened_to_names(self, mock_post):
        """FortiManager may return members as objects rather than bare names."""
        _, by_name = self._run_against_fixture(mock_post)

        self.assertEqual(by_name["member-objects-group"]["member"], ["internal-net", "example-fqdn"])

    @patch("requests.post")
    def test_comment_returned_as_list_is_collapsed(self, mock_post):
        """A comment returned as a list becomes a string rather than failing validation."""
        _, by_name = self._run_against_fixture(mock_post)

        self.assertEqual(by_name["member-objects-group"]["comment"], "Comment returned as a list")

    @patch("requests.post")
    def test_single_bare_string_member_becomes_a_list(self, mock_post):
        """A lone member returned as a bare string is wrapped into a list."""
        _, by_name = self._run_against_fixture(mock_post)

        self.assertEqual(by_name["single-member-group"]["member"], ["google-dns"])

    @patch("requests.post")
    def test_empty_group_keeps_required_member_field(self, mock_post):
        """A group with no members still emits member as an empty list."""
        _, by_name = self._run_against_fixture(mock_post)

        self.assertEqual(by_name["empty-group"]["member"], [])

    @patch("requests.post")
    def test_undeclared_fields_are_dropped(self, mock_post):
        """uuid and color are not part of the declared type and must not be emitted."""
        result, _ = self._run_against_fixture(mock_post)

        for group in result[Output.ADDRESS_GROUPS]:
            self.assertFalse({"uuid", "color"} & set(group))

    @patch("requests.post")
    def test_empty_adom_returns_empty_list(self, mock_post):
        """An ADOM with no groups returns an empty list rather than erroring."""
        mock_post.return_value = MockResponse(
            {"id": 1, "result": [{"status": {"code": 0, "message": "OK"}, "data": []}]}
        )

        result = self.action.run({})

        self.assertEqual(result[Output.ADDRESS_GROUPS], [])
        self.assertIn("0 address groups", result[Output.MESSAGE])
        validate(result, ListAddressGroupsOutput.schema)

    @patch("requests.post")
    def test_uses_list_endpoint_and_honors_adom_override(self, mock_post):
        """The addrgrp list endpoint is used and the ADOM input overrides the default."""
        mock_post.return_value = MockResponse(load_payload("get_address_groups.json.resp"))

        self.action.run({Input.ADOM: "custom-adom"})

        payload = mock_post.call_args[1].get("json") or mock_post.call_args[0][0]
        url = payload["params"][0]["url"]
        self.assertIn("custom-adom", url)
        self.assertTrue(url.endswith("/obj/firewall/addrgrp"))
