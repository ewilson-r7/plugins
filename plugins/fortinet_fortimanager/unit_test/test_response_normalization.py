"""Regression coverage for FortiManager response normalization.

Every crash reported against 2.1.0 was an output schema violation caused by
FortiManager returning loosely typed values, and every one of them passed the unit
suite because the fixtures used idealized shapes (`type` as a string, `subnet` as a
CIDR string) that the real API never sends. These tests assert against the wire
format and validate action output against the generated schema.
"""

import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

from jsonschema import validate

from icon_fortinet_fortimanager.actions.get_address_objects import GetAddressObjects
from icon_fortinet_fortimanager.actions.get_address_objects.schema import (
    GetAddressObjectsOutput,
    Input as GetInput,
    Output as GetOutput,
)
from icon_fortinet_fortimanager.actions.remove_address_object_from_group import RemoveAddressObjectFromGroup
from icon_fortinet_fortimanager.actions.remove_address_object_from_group.schema import (
    RemoveAddressObjectFromGroupOutput,
    Input as RemoveInput,
    Output as RemoveOutput,
)
from icon_fortinet_fortimanager.util.helpers import Helpers
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestAddressObjectNormalizer(TestCase):
    def test_subnet_list_becomes_cidr(self):
        """FortiManager's address-plus-netmask list is collapsed to CIDR."""
        result = Helpers.normalize_address_object(
            {"name": "host", "type": 0, "subnet": ["198.51.100.100", "255.255.255.255"]}
        )

        self.assertEqual(result["subnet"], "198.51.100.100/32")
        self.assertIsInstance(result["subnet"], str)

    def test_wider_netmask_becomes_correct_prefix(self):
        """A non-/32 netmask converts to the matching prefix length."""
        result = Helpers.normalize_address_object(
            {"name": "net", "type": 0, "subnet": ["192.168.1.0", "255.255.255.0"]}
        )

        self.assertEqual(result["subnet"], "192.168.1.0/24")

    def test_integer_type_becomes_name(self):
        """The integer type encoding is mapped to the string name the schema declares."""
        self.assertEqual(Helpers.normalize_address_object({"name": "a", "type": 0})["type"], "ipmask")
        self.assertEqual(Helpers.normalize_address_object({"name": "b", "type": 1})["type"], "iprange")
        self.assertEqual(Helpers.normalize_address_object({"name": "c", "type": 2})["type"], "fqdn")

    def test_string_type_passes_through(self):
        """A type already returned as a string is preserved."""
        self.assertEqual(Helpers.normalize_address_object({"name": "a", "type": "ipmask"})["type"], "ipmask")

    def test_unmapped_integer_type_is_coerced_not_guessed(self):
        """An unknown type ID becomes a string rather than crashing or being mislabelled."""
        result = Helpers.normalize_address_object({"name": "a", "type": 99, "subnet": ["10.0.0.1", "255.255.255.255"]})

        self.assertEqual(result["type"], "99")
        self.assertIsInstance(result["type"], str)

    def test_absent_type_is_inferred_from_value_fields(self):
        """When the API omits type entirely it is inferred from the value present."""
        self.assertEqual(Helpers.normalize_address_object({"name": "a", "fqdn": "example.com"})["type"], "fqdn")
        self.assertEqual(
            Helpers.normalize_address_object({"name": "b", "start-ip": "203.0.113.1", "end-ip": "203.0.113.9"})["type"],
            "iprange",
        )

    def test_hyphenated_api_fields_map_to_schema_names(self):
        """start-ip/end-ip/associated-interface populate the underscored schema fields."""
        result = Helpers.normalize_address_object(
            {
                "name": "range",
                "type": 1,
                "start-ip": "203.0.113.10",
                "end-ip": "203.0.113.20",
                "associated-interface": ["port1"],
            }
        )

        self.assertEqual(result["start_ip"], "203.0.113.10")
        self.assertEqual(result["end_ip"], "203.0.113.20")
        self.assertEqual(result["associated_interface"], "port1")

    def test_undeclared_api_fields_are_dropped(self):
        """Fields outside the declared type are not emitted, so new API fields cannot break output."""
        result = Helpers.normalize_address_object(
            {"name": "a", "type": 0, "uuid": "x", "color": 0, "allow-routing": 0, "unexpected": ["deeply", "nested"]}
        )

        self.assertEqual(set(result), {"name", "type"})

    def test_required_fields_always_present(self):
        """name and type are always emitted because the schema marks them required."""
        for payload in ({}, {"subnet": None}, {"name": None, "type": None}):
            result = Helpers.normalize_address_object(payload)
            self.assertIn("name", result)
            self.assertIn("type", result)

    def test_non_dict_input_is_survivable(self):
        """A malformed entry yields a schema-valid stub instead of raising."""
        self.assertEqual(Helpers.normalize_address_object(None), {"name": "", "type": ""})


class TestOutputSchemaConformance(TestCase):
    """Validate action output against the generated schema using real wire-format data."""

    @patch("requests.post")
    def test_get_address_objects_output_matches_schema(self, mock_post):
        """Reproduces the '0 is not of type string' crash from 2.1.0."""
        action = GetAddressObjects()
        action.connection = create_mock_connection()
        action.logger = action.connection.logger
        mock_post.return_value = MockResponse(load_payload("get_address_objects.json.resp"))

        result = action.run({})

        validate(result, GetAddressObjectsOutput.schema)
        for address_object in result[GetOutput.ADDRESS_OBJECTS]:
            self.assertIsInstance(address_object["type"], str)
            self.assertIsInstance(address_object.get("subnet", ""), str)

    @patch("requests.post")
    def test_name_filter_output_matches_schema(self, mock_post):
        """The Name Filter path is the one the customer reported as crashing."""
        action = GetAddressObjects()
        action.connection = create_mock_connection()
        action.logger = action.connection.logger
        mock_post.return_value = MockResponse(load_payload("get_address_objects.json.resp"))

        result = action.run({GetInput.NAME_FILTER: "google-dns"})

        self.assertEqual(len(result[GetOutput.ADDRESS_OBJECTS]), 1)
        validate(result, GetAddressObjectsOutput.schema)

    @patch("requests.post")
    def test_subnet_filter_matches_netmask_form(self, mock_post):
        """A CIDR filter matches an object stored in address-plus-netmask form."""
        action = GetAddressObjects()
        action.connection = create_mock_connection()
        action.logger = action.connection.logger
        mock_post.return_value = MockResponse(load_payload("get_address_objects.json.resp"))

        result = action.run({GetInput.SUBNET_FILTER: "8.8.8.8/32"})

        self.assertEqual(len(result[GetOutput.ADDRESS_OBJECTS]), 1)
        self.assertEqual(result[GetOutput.ADDRESS_OBJECTS][0]["name"], "google-dns")
        validate(result, GetAddressObjectsOutput.schema)

    @patch("requests.post")
    def test_remove_from_group_output_matches_schema(self, mock_post):
        """Both the removed and the not-a-member paths conform to the schema."""
        action = RemoveAddressObjectFromGroup()
        action.connection = create_mock_connection()
        action.logger = action.connection.logger
        mock_post.side_effect = [
            MockResponse(load_payload("get_address_group.json.resp")),
            MockResponse(load_payload("update_address_group.json.resp")),
        ]

        result = action.run({RemoveInput.ADDRESS_OBJECT: "google-dns", RemoveInput.GROUP: "blocked-addresses"})

        self.assertTrue(result[RemoveOutput.SUCCESS])
        self.assertIn("removed from group", result[RemoveOutput.MESSAGE])
        validate(result, RemoveAddressObjectFromGroupOutput.schema)

    @patch("requests.post")
    def test_remove_non_member_output_matches_schema(self, mock_post):
        """A non-member is reported through the output and stays schema-valid."""
        action = RemoveAddressObjectFromGroup()
        action.connection = create_mock_connection()
        action.logger = action.connection.logger
        mock_post.side_effect = [MockResponse(load_payload("get_address_group.json.resp"))]

        result = action.run({RemoveInput.ADDRESS_OBJECT: "not-a-member", RemoveInput.GROUP: "blocked-addresses"})

        self.assertFalse(result[RemoveOutput.SUCCESS])
        self.assertIn("not a member", result[RemoveOutput.MESSAGE])
        validate(result, RemoveAddressObjectFromGroupOutput.schema)
