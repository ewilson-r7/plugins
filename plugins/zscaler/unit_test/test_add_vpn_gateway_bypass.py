import sys
import os

sys.path.append(os.path.abspath("../"))

import json
import time
import logging
from unittest import TestCase
from unittest.mock import Mock, patch

from icon_zscaler.util.zcc_client import ZCCClient


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


def _mock_response(status_code=200, json_data=None):
    resp = Mock()
    resp.status_code = status_code
    resp.text = json.dumps(json_data if json_data is not None else {})
    resp.headers = {}
    resp.json.return_value = json_data if json_data is not None else {}
    return resp


class TestAddVpnGatewayBypass(TestCase):

    @patch("requests.request")
    def test_adds_entry_to_profile(self, mock_request):
        """Test add_vpn_gateway_bypass adds an entry and returns updated list."""
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

        result = client.add_vpn_gateway_bypass("profile-001", "vpn2.example.com")

        self.assertTrue(result["success"])
        self.assertEqual(len(result["vpn_gateways"]), 2)
        hostnames = [gw["hostname"] for gw in result["vpn_gateways"]]
        self.assertIn("vpn2.example.com", hostnames)

    @patch("requests.request")
    def test_idempotent_when_entry_exists(self, mock_request):
        """Test that adding an existing entry does not duplicate it."""
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
        ]
        client = _make_zcc_client()

        result = client.add_vpn_gateway_bypass("profile-001", "vpn1.example.com")

        self.assertTrue(result["success"])
        self.assertEqual(len(result["vpn_gateways"]), 1)
        # No PATCH call should have been made
        self.assertEqual(mock_request.call_count, 1)

    @patch("requests.request")
    def test_patch_includes_numeric_device_type(self, mock_request):
        """Test that PATCH body includes deviceType as numeric ID."""
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

        client.add_vpn_gateway_bypass("profile-001", "new-gw.example.com")

        patch_call = mock_request.call_args_list[1]
        patch_kwargs = patch_call[1]
        patch_data = json.loads(patch_kwargs["data"])
        self.assertEqual(patch_data["deviceType"], 3)

    @patch("requests.request")
    def test_adds_to_empty_gateways_list(self, mock_request):
        """Test adding to a profile with empty vpnGateways."""
        list_response = {
            "profiles": [
                {
                    "profileId": "profile-001",
                    "profileName": "Default Profile",
                    "deviceType": "DEVICE_TYPE_MACOS",
                    "policyExtension": {
                        "vpnGateways": []
                    },
                }
            ]
        }
        mock_request.side_effect = [
            _mock_response(200, list_response),
            _mock_response(200, {}),
        ]
        client = _make_zcc_client()

        result = client.add_vpn_gateway_bypass("profile-001", "new-gw.example.com")

        self.assertTrue(result["success"])
        self.assertEqual(len(result["vpn_gateways"]), 1)
        self.assertEqual(result["vpn_gateways"][0]["hostname"], "new-gw.example.com")
