import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

from insightconnect_plugin_runtime.exceptions import PluginException
from jsonschema import validate

from icon_fortinet_fortimanager.actions.get_address_group import GetAddressGroup
from icon_fortinet_fortimanager.actions.get_address_group.schema import GetAddressGroupOutput, Input, Output
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestGetAddressGroup(TestCase):
    def setUp(self):
        self.action = GetAddressGroup()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

    @staticmethod
    def _group_response(data: dict) -> dict:
        return {"id": 1, "result": [{"status": {"code": 0, "message": "OK"}, "data": data}]}

    @patch("requests.post")
    def test_get_address_group_returns_member_names(self, mock_post):
        """The group is returned with its member names."""
        mock_post.return_value = MockResponse(load_payload("get_address_group.json.resp"))

        result = self.action.run({Input.GROUP: "blocked-addresses"})

        group = result[Output.ADDRESS_GROUP]
        self.assertEqual(group["name"], "blocked-addresses")
        self.assertEqual(group["member"], ["google-dns", "cloudflare-dns"])
        self.assertEqual(group["comment"], "Blocked address group")
        self.assertIn("2 members", result[Output.MESSAGE])
        validate(result, GetAddressGroupOutput.schema)

    @patch("requests.post")
    def test_members_returned_as_objects_are_flattened_to_names(self, mock_post):
        """FortiManager may return members as objects rather than bare names."""
        mock_post.return_value = MockResponse(
            self._group_response({"name": "g", "member": [{"name": "internal-net"}, {"name": "example-fqdn"}]})
        )

        result = self.action.run({Input.GROUP: "g"})

        self.assertEqual(result[Output.ADDRESS_GROUP]["member"], ["internal-net", "example-fqdn"])
        validate(result, GetAddressGroupOutput.schema)

    @patch("requests.post")
    def test_single_bare_string_member_becomes_a_list(self, mock_post):
        """A lone member returned as a bare string is wrapped into a list."""
        mock_post.return_value = MockResponse(self._group_response({"name": "solo", "member": "google-dns"}))

        result = self.action.run({Input.GROUP: "solo"})

        self.assertEqual(result[Output.ADDRESS_GROUP]["member"], ["google-dns"])
        self.assertIn("1 member.", result[Output.MESSAGE])
        validate(result, GetAddressGroupOutput.schema)

    @patch("requests.post")
    def test_empty_group_is_schema_valid(self, mock_post):
        """A group with no members still satisfies the required member field."""
        mock_post.return_value = MockResponse(self._group_response({"name": "empty-group", "member": []}))

        result = self.action.run({Input.GROUP: "empty-group"})

        self.assertEqual(result[Output.ADDRESS_GROUP]["member"], [])
        self.assertIn("0 members", result[Output.MESSAGE])
        validate(result, GetAddressGroupOutput.schema)

    @patch("requests.post")
    def test_undeclared_fields_are_dropped(self, mock_post):
        """Fields outside the declared type are not emitted."""
        mock_post.return_value = MockResponse(
            self._group_response({"name": "g", "member": [], "uuid": "x", "color": 3})
        )

        result = self.action.run({Input.GROUP: "g"})

        self.assertEqual(set(result[Output.ADDRESS_GROUP]), {"name", "member"})

    @patch("requests.post")
    def test_group_not_found_raises_exception(self, mock_post):
        """A missing group is a genuine failure and raises."""
        mock_post.return_value = MockResponse(load_payload("error_object_not_exist.json.resp"))

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.GROUP: "nonexistent-group"})

        self.assertIn("-3", context.exception.cause)

    @patch("requests.post")
    def test_adom_override(self, mock_post):
        """The ADOM input overrides the connection default."""
        mock_post.return_value = MockResponse(load_payload("get_address_group.json.resp"))

        self.action.run({Input.GROUP: "blocked-addresses", Input.ADOM: "custom-adom"})

        payload = mock_post.call_args[1].get("json") or mock_post.call_args[0][0]
        self.assertIn("custom-adom", payload["params"][0]["url"])
