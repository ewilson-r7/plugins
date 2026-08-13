import os
import sys

sys.path.append(os.path.abspath("../"))

import json
from unittest import TestCase
from unittest.mock import patch

import requests
from icon_zscaler.util.zcc_client import (
    ZCCClient,
    extract_gateway_entries,
    normalize_gateway_entry,
    normalize_profile_id,
)
from parameterized import parameterized
from util import Util


class MockResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text

    def json(self):
        return json.loads(self.text)


def create_client() -> ZCCClient:
    import logging

    client = ZCCClient("test-client-id", "unused", "testcompany", "zsapi.net", logging.getLogger("test"))
    client._token = "mock-access-token-12345"
    client._token_expiry = 9999999999
    return client


class TestNormalizeGatewayEntry(TestCase):
    """Zscaler returns vpnGateways as strings in some tenants and objects in others."""

    @parameterized.expand(
        [
            ("hostname_string", "vpn1.example.com", {"hostname": "vpn1.example.com", "ip": "", "type": "hostname"}),
            ("ipv4_string", "10.0.0.1", {"hostname": "", "ip": "10.0.0.1", "type": "ip"}),
            ("cidr_string", "10.0.0.0/24", {"hostname": "", "ip": "10.0.0.0/24", "type": "ip"}),
            ("ipv6_string", "2001:db8::1", {"hostname": "", "ip": "2001:db8::1", "type": "ip"}),
        ]
    )
    def test_normalizes_string_entries(self, _name, entry, expected) -> None:
        self.assertEqual(normalize_gateway_entry(entry), expected)

    def test_normalizes_dict_entries(self) -> None:
        entry = {"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"}
        self.assertEqual(normalize_gateway_entry(entry), entry)

    def test_defaults_missing_dict_fields(self) -> None:
        self.assertEqual(
            normalize_gateway_entry({"hostname": "vpn1.example.com"}),
            {"hostname": "vpn1.example.com", "ip": "", "type": ""},
        )


class TestNormalizeProfileId(TestCase):
    """Zscaler returns profileId as a JSON number, so 14729 arrives as the float 14729.0."""

    @parameterized.expand(
        [
            ("whole_float", 14729.0, "14729"),
            ("int", 1007, "1007"),
            ("float_string", "14729.0", "14729"),
            ("plain_string", "14729", "14729"),
            ("padded_string", " 1007.0 ", "1007"),
            ("multi_zero_decimal", "1007.00", "1007"),
            ("non_numeric_id", "profile-001", "profile-001"),
            ("empty", "", ""),
        ]
    )
    def test_renders_without_trailing_decimal(self, _name, value, expected) -> None:
        self.assertEqual(normalize_profile_id(value), expected)

    def test_preserves_meaningful_decimal(self) -> None:
        """Only whole numbers are truncated, so a genuine fraction is left intact."""
        self.assertEqual(normalize_profile_id("14729.5"), "14729.5")


class TestExtractGatewayEntries(TestCase):
    """vpnGateways arrives as a comma separated string in some tenants and a list in others."""

    def test_splits_comma_separated_string(self) -> None:
        entries, was_string = extract_gateway_entries({"vpnGateways": "172.16.0.0/12,10.0.0.0/8"})
        self.assertEqual(entries, ["172.16.0.0/12", "10.0.0.0/8"])
        self.assertTrue(was_string)

    def test_strips_whitespace_and_empty_segments(self) -> None:
        entries, _ = extract_gateway_entries({"vpnGateways": " 10.0.0.1 , ,vpn.example.com,"})
        self.assertEqual(entries, ["10.0.0.1", "vpn.example.com"])

    def test_single_string_value_is_not_split_into_characters(self) -> None:
        """Regression: iterating the string directly yielded one entry per character."""
        entries, was_string = extract_gateway_entries({"vpnGateways": "172.16.0.0/12"})
        self.assertEqual(entries, ["172.16.0.0/12"])
        self.assertTrue(was_string)

    def test_passes_list_through_unchanged(self) -> None:
        entries, was_string = extract_gateway_entries({"vpnGateways": ["10.0.0.1"]})
        self.assertEqual(entries, ["10.0.0.1"])
        self.assertFalse(was_string)

    @parameterized.expand([("missing", {}), ("none", {"vpnGateways": None}), ("empty_string", {"vpnGateways": ""})])
    def test_returns_empty_for_absent_values(self, _name, policy_extension) -> None:
        self.assertEqual(extract_gateway_entries(policy_extension), ([], False))


class TestGetVpnGatewayBypassesStringShape(TestCase):
    def test_parses_string_gateways_without_error(self) -> None:
        """Regression: string entries previously raised AttributeError on gw.get()."""
        fixture = Util.read_file_to_string("responses/zcc_list_by_company_string_gateways.json.resp")

        with patch.object(requests, "request", return_value=MockResponse(200, fixture)):
            result = create_client().get_vpn_gateway_bypasses()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["profile_id"], "profile-101")
        self.assertEqual(
            result[0]["vpn_gateways"],
            [
                {"hostname": "vpn1.example.com", "ip": "", "type": "hostname"},
                {"hostname": "", "ip": "10.0.0.1", "type": "ip"},
                {"hostname": "", "ip": "10.0.0.0/24", "type": "ip"},
            ],
        )

    def test_parses_comma_separated_string_gateways(self) -> None:
        """Reproduces the customer's tenant, where vpnGateways is a single string."""
        fixture = json.dumps(
            {
                "profiles": [
                    {
                        "profileId": "1007.0",
                        "profileName": "MNP Z-Tunnel 2.0 General",
                        "policyExtension": {"vpnGateways": "172.16.0.0/12,vpn.example.com"},
                    }
                ]
            }
        )

        with patch.object(requests, "request", return_value=MockResponse(200, fixture)):
            result = create_client().get_vpn_gateway_bypasses()

        self.assertEqual(result[0]["profile_id"], "1007")
        self.assertEqual(result[0]["profile_name"], "MNP Z-Tunnel 2.0 General")
        self.assertEqual(
            result[0]["vpn_gateways"],
            [
                {"hostname": "", "ip": "172.16.0.0/12", "type": "ip"},
                {"hostname": "vpn.example.com", "ip": "", "type": "hostname"},
            ],
        )

    def test_strips_trailing_decimal_from_profile_id(self) -> None:
        """The API returns profileId as a number, which must not surface as 14729.0."""
        fixture = json.dumps(
            {
                "profiles": [
                    {
                        "profileId": 14729.0,
                        "profileName": "Stepan Test",
                        "policyExtension": {"vpnGateways": "calgary.vpn.mnp.ca"},
                    }
                ]
            }
        )

        with patch.object(requests, "request", return_value=MockResponse(200, fixture)):
            result = create_client().get_vpn_gateway_bypasses()

        self.assertEqual(result[0]["profile_id"], "14729")

    def test_output_keys_match_schema(self) -> None:
        """The vpn_gateway_profile type requires snake_case keys."""
        fixture = Util.read_file_to_string("responses/zcc_list_by_company_string_gateways.json.resp")

        with patch.object(requests, "request", return_value=MockResponse(200, fixture)):
            result = create_client().get_vpn_gateway_bypasses()

        self.assertEqual(set(result[0]), {"profile_id", "profile_name", "vpn_gateways"})


class TestRemoveVpnGatewayBypassStringShape(TestCase):
    def _run_removal(self, entry_to_remove: str):
        fixture = Util.read_file_to_string("responses/zcc_list_by_company_string_gateways.json.resp")
        calls = []

        def fake_request(method=None, url=None, **kwargs):
            calls.append({"method": method, "url": url, **kwargs})
            if method == "GET":
                return MockResponse(200, fixture)
            return MockResponse(200, "{}")

        with patch.object(requests, "request", side_effect=fake_request):
            result = create_client().remove_vpn_gateway_bypass("profile-101", entry_to_remove)

        return result, calls

    def test_removes_matching_hostname_string(self) -> None:
        result, calls = self._run_removal("vpn1.example.com")

        self.assertTrue(result["success"])
        # Returned entries are normalized objects to match the vpn_gateway_entry type
        self.assertEqual(
            result["vpn_gateways"],
            [
                {"hostname": "", "ip": "10.0.0.1", "type": "ip"},
                {"hostname": "", "ip": "10.0.0.0/24", "type": "ip"},
            ],
        )
        # The PATCH preserves the tenant's original list shape
        patch_call = [call for call in calls if call["method"] == "PATCH"][0]
        self.assertEqual(json.loads(patch_call["data"]), {"vpnGateways": ["10.0.0.1", "10.0.0.0/24"]})

    def test_removes_matching_ip_string(self) -> None:
        result, _ = self._run_removal("10.0.0.1")
        self.assertEqual(
            result["vpn_gateways"],
            [
                {"hostname": "vpn1.example.com", "ip": "", "type": "hostname"},
                {"hostname": "", "ip": "10.0.0.0/24", "type": "ip"},
            ],
        )

    def test_leaves_list_untouched_when_no_match(self) -> None:
        result, _ = self._run_removal("not-present.example.com")
        self.assertEqual(len(result["vpn_gateways"]), 3)

    @parameterized.expand([("without_decimal", "14729"), ("with_decimal", "14729.0")])
    def test_patch_url_omits_trailing_decimal(self, _name, supplied_profile_id) -> None:
        """Either form of the ID must resolve and produce a clean request path."""
        fixture = json.dumps(
            {
                "profiles": [
                    {
                        "profileId": 14729.0,
                        "policyExtension": {"vpnGateways": "calgary.vpn.mnp.ca,10.0.0.1"},
                    }
                ]
            }
        )
        calls = []

        def fake_request(method=None, url=None, **kwargs):
            calls.append({"method": method, "url": url, **kwargs})
            return MockResponse(200, fixture if method == "GET" else "{}")

        with patch.object(requests, "request", side_effect=fake_request):
            result = create_client().remove_vpn_gateway_bypass(supplied_profile_id, "10.0.0.1")

        patch_call = [call for call in calls if call["method"] == "PATCH"][0]
        self.assertEqual(
            patch_call["url"],
            "https://api.zsapi.net/zcc/papi/public/v1/application-profiles/14729",
        )
        # Profile was actually located, so the entry was removed rather than no-oping
        self.assertEqual(result["vpn_gateways"], [{"hostname": "calgary.vpn.mnp.ca", "ip": "", "type": "hostname"}])

    def test_writes_back_as_string_when_tenant_uses_string(self) -> None:
        """A string-valued vpnGateways must be PATCHed back as a string, not a list."""
        fixture = json.dumps(
            {
                "profiles": [
                    {
                        "profileId": "1007.0",
                        "policyExtension": {"vpnGateways": "172.16.0.0/12,vpn.example.com"},
                    }
                ]
            }
        )
        calls = []

        def fake_request(method=None, url=None, **kwargs):
            calls.append({"method": method, "url": url, **kwargs})
            return MockResponse(200, fixture if method == "GET" else "{}")

        with patch.object(requests, "request", side_effect=fake_request):
            result = create_client().remove_vpn_gateway_bypass("1007.0", "vpn.example.com")

        patch_call = [call for call in calls if call["method"] == "PATCH"][0]
        self.assertEqual(json.loads(patch_call["data"]), {"vpnGateways": "172.16.0.0/12"})
        self.assertEqual(result["vpn_gateways"], [{"hostname": "", "ip": "172.16.0.0/12", "type": "ip"}])
