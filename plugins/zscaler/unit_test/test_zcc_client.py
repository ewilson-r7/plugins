"""
Unit tests for ZCCClient (VPN gateway bypass operations).
"""

import os
import sys
import json
import time
import logging
from unittest import TestCase
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath("../"))

from icon_zscaler.util.zcc_client import ZCCClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_zcc_client():
    client = ZCCClient(
        client_id="test-client-id",
        private_key="fake-private-key",
        vanity_domain="mycompany",
        cloud="zsapi.net",
        logger=logging.getLogger("test"),
    )
    client._token = "pre-seeded-token"
    client._token_expiry = int(time.time()) + 3600
    return client


def _mock_response(status_code=200, json_data=None, text=""):
    resp = Mock()
    resp.status_code = status_code
    resp.text = text or json.dumps(json_data if json_data is not None else {})
    resp.headers = {}
    resp.json.return_value = json_data if json_data is not None else {}
    return resp


# ---------------------------------------------------------------------------
# get_vpn_gateway_bypasses tests
# ---------------------------------------------------------------------------


class TestGetVpnGatewayBypasses(TestCase):

    @patch("requests.request")
    def test_parses_vpn_gateways_correctly(self, mock_request):
        """Test that get_vpn_gateway_bypasses parses policyExtension.vpnGateways correctly from response."""
        api_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Default Profile",
                    "policyExtension": {
                        "vpnGateways": [
                            {"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"},
                            {"hostname": "vpn2.example.com", "ip": "10.0.0.2", "type": "ip"},
                        ]
                    },
                }
            ]
        }
        mock_request.return_value = _mock_response(200, api_response)
        client = _make_zcc_client()

        result = client.get_vpn_gateway_bypasses()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["profile_id"], "profile-001")
        self.assertEqual(result[0]["profile_name"], "Default Profile")
        self.assertEqual(len(result[0]["vpn_gateways"]), 2)
        self.assertEqual(result[0]["vpn_gateways"][0]["hostname"], "vpn1.example.com")
        self.assertEqual(result[0]["vpn_gateways"][0]["ip"], "10.0.0.1")
        self.assertEqual(result[0]["vpn_gateways"][0]["type"], "hostname")
        self.assertEqual(result[0]["vpn_gateways"][1]["hostname"], "vpn2.example.com")

    @patch("requests.request")
    def test_skips_profiles_with_empty_vpn_gateways(self, mock_request):
        """Test that profiles with empty vpnGateways list are skipped."""
        api_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Has Gateways",
                    "policyExtension": {
                        "vpnGateways": [{"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"}]
                    },
                },
                {
                    "profileId": "profile-002",
                    "profileName": "Empty VPN Profile",
                    "policyExtension": {"vpnGateways": []},
                },
            ]
        }
        mock_request.return_value = _mock_response(200, api_response)
        client = _make_zcc_client()

        result = client.get_vpn_gateway_bypasses()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["profile_id"], "profile-001")

    @patch("requests.request")
    def test_skips_profiles_missing_policy_extension(self, mock_request):
        """Test that profiles missing the policyExtension field are skipped."""
        api_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Has Gateways",
                    "policyExtension": {
                        "vpnGateways": [{"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"}]
                    },
                },
                {"profileId": "profile-003", "profileName": "No Extension Profile"},
            ]
        }
        mock_request.return_value = _mock_response(200, api_response)
        client = _make_zcc_client()

        result = client.get_vpn_gateway_bypasses()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["profile_id"], "profile-001")

    @patch("requests.request")
    def test_handles_list_response_format(self, mock_request):
        """Test that a plain list response (not wrapped in dict) is handled."""
        api_response = [
            {
                "profileId": "profile-001",
                "profileName": "Profile A",
                "policyExtension": {
                    "vpnGateways": [{"hostname": "gw.example.com", "ip": "192.168.1.1", "type": "hostname"}]
                },
            }
        ]
        mock_request.return_value = _mock_response(200, api_response)
        client = _make_zcc_client()

        result = client.get_vpn_gateway_bypasses()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["profile_name"], "Profile A")


# ---------------------------------------------------------------------------
# remove_vpn_gateway_bypass tests
# ---------------------------------------------------------------------------


class TestRemoveVpnGatewayBypass(TestCase):

    @patch("requests.request")
    def test_removes_entry_by_hostname(self, mock_request):
        """Test remove_vpn_gateway_bypass removes an entry matching by hostname and returns updated list."""
        list_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Default Profile",
                    "deviceType": "DEVICE_TYPE_WINDOWS",
                    "policyExtension": {
                        "vpnGateways": [
                            {"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"},
                            {"hostname": "vpn2.example.com", "ip": "10.0.0.2", "type": "ip"},
                        ]
                    },
                }
            ]
        }
        # First call is GET listByCompany, second is PATCH
        mock_request.side_effect = [
            _mock_response(200, list_response),
            _mock_response(200, {}),
        ]
        client = _make_zcc_client()

        result = client.remove_vpn_gateway_bypass("profile-001", "vpn1.example.com")

        self.assertTrue(result["success"])
        self.assertEqual(len(result["vpn_gateways"]), 1)
        self.assertEqual(result["vpn_gateways"][0]["hostname"], "vpn2.example.com")

        # Verify PATCH was called with correct payload
        patch_call = mock_request.call_args_list[1]
        patch_kwargs = patch_call[1]
        self.assertIn("PATCH", patch_kwargs.get("method", ""))
        patch_data = json.loads(patch_kwargs["data"])
        self.assertIn("policyExtension", patch_data)
        self.assertEqual(len(patch_data["policyExtension"]["vpnGateways"]), 1)

    @patch("requests.request")
    def test_removes_entry_by_ip(self, mock_request):
        """Test remove_vpn_gateway_bypass removes an entry matching by IP."""
        list_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Default Profile",
                    "deviceType": "DEVICE_TYPE_WINDOWS",
                    "policyExtension": {
                        "vpnGateways": [
                            {"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"},
                            {"hostname": "vpn2.example.com", "ip": "10.0.0.2", "type": "ip"},
                        ]
                    },
                }
            ]
        }
        mock_request.side_effect = [
            _mock_response(200, list_response),
            _mock_response(200, {}),
        ]
        client = _make_zcc_client()

        result = client.remove_vpn_gateway_bypass("profile-001", "10.0.0.1")

        self.assertTrue(result["success"])
        self.assertEqual(len(result["vpn_gateways"]), 1)
        self.assertEqual(result["vpn_gateways"][0]["ip"], "10.0.0.2")

    @patch("requests.request")
    def test_constructs_patch_payload_with_device_type(self, mock_request):
        """Test that PATCH payload includes deviceType converted from string to numeric ID."""
        list_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Default Profile",
                    "deviceType": "DEVICE_TYPE_WINDOWS",
                    "policyExtension": {
                        "vpnGateways": [
                            {"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"},
                        ]
                    },
                }
            ]
        }
        mock_request.side_effect = [
            _mock_response(200, list_response),
            _mock_response(200, {}),
        ]
        client = _make_zcc_client()

        client.remove_vpn_gateway_bypass("profile-001", "vpn1.example.com")

        patch_call = mock_request.call_args_list[1]
        patch_kwargs = patch_call[1]
        patch_data = json.loads(patch_kwargs["data"])
        # PATCH must include deviceType as numeric ID (3 = Windows)
        self.assertIn("policyExtension", patch_data)
        self.assertIn("vpnGateways", patch_data["policyExtension"])
        self.assertIn("deviceType", patch_data)
        self.assertEqual(patch_data["deviceType"], 3)

    @patch("requests.request")
    def test_entry_not_found_is_idempotent(self, mock_request):
        """Test remove with entry that doesn't exist returns success=True (idempotent no-op)."""
        list_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Default Profile",
                    "deviceType": "DEVICE_TYPE_WINDOWS",
                    "policyExtension": {
                        "vpnGateways": [
                            {"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"},
                        ]
                    },
                }
            ]
        }
        mock_request.side_effect = [
            _mock_response(200, list_response),
            _mock_response(200, {}),
        ]
        client = _make_zcc_client()

        result = client.remove_vpn_gateway_bypass("profile-001", "nonexistent.example.com")

        self.assertTrue(result["success"])
        # Original entry should remain since no match was found
        self.assertEqual(len(result["vpn_gateways"]), 1)

    @patch("requests.request")
    def test_empty_vpn_gateways_returns_success(self, mock_request):
        """Test remove with empty vpnGateways list returns success=True with empty list."""
        list_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Default Profile",
                    "policyExtension": {"vpnGateways": []},
                }
            ]
        }
        mock_request.return_value = _mock_response(200, list_response)
        client = _make_zcc_client()

        result = client.remove_vpn_gateway_bypass("profile-001", "vpn1.example.com")

        self.assertTrue(result["success"])
        self.assertEqual(result["vpn_gateways"], [])

    @patch("requests.request")
    def test_profile_not_found_returns_success(self, mock_request):
        """Test remove with profile that doesn't exist returns success=True with empty list."""
        list_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Default Profile",
                    "policyExtension": {
                        "vpnGateways": [{"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"}]
                    },
                }
            ]
        }
        mock_request.return_value = _mock_response(200, list_response)
        client = _make_zcc_client()

        result = client.remove_vpn_gateway_bypass("nonexistent-profile-id", "vpn1.example.com")

        self.assertTrue(result["success"])
        self.assertEqual(result["vpn_gateways"], [])


# ---------------------------------------------------------------------------
# test() connectivity
# ---------------------------------------------------------------------------


class TestZCCClientTest(TestCase):

    @patch("requests.request")
    def test_calls_correct_endpoint(self, mock_request):
        """Test that test() calls GET web/policy/listByCompany endpoint."""
        mock_request.return_value = _mock_response(200, {"profiles": []})
        client = _make_zcc_client()

        result = client.test()

        self.assertEqual(result, {"success": True})
        call_kwargs = mock_request.call_args[1]
        self.assertIn("/zcc/papi/public/v1/web/policy/listByCompany", call_kwargs["url"])
        self.assertEqual(call_kwargs["method"], "GET")
        self.assertEqual(call_kwargs["headers"]["Authorization"], "Bearer pre-seeded-token")
