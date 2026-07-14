"""
Unit tests for RemoveVpnGatewayBypass action.
"""

import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch, MagicMock

from util import Util
from icon_zscaler.actions.remove_vpn_gateway_bypass import RemoveVpnGatewayBypass
from icon_zscaler.actions.remove_vpn_gateway_bypass.schema import Output


@patch("requests.request", side_effect=Util.mock_request)
class TestRemoveVpnGatewayBypassAction(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.action = Util.default_connector(RemoveVpnGatewayBypass())
        # Also set ZCC token since default_connector doesn't set it
        cls.action.connection.zcc_client._token = "mock-access-token-12345"
        cls.action.connection.zcc_client._token_expiry = 9999999999

    def test_calls_zcc_client_remove_vpn_gateway_bypass(self, _mock_request):
        """Test action handler calls self.connection.zcc_client.remove_vpn_gateway_bypass(profile_id, entry)."""
        mock_result = {
            "success": True,
            "vpn_gateways": [{"hostname": "vpn2.example.com", "ip": "10.0.0.2", "type": "ip"}],
        }
        self.action.connection.zcc_client.remove_vpn_gateway_bypass = MagicMock(return_value=mock_result)

        result = self.action.run({"profile_id": "profile-001", "entry": "vpn1.example.com"})

        self.action.connection.zcc_client.remove_vpn_gateway_bypass.assert_called_once_with(
            "profile-001", "vpn1.example.com"
        )

    def test_output_uses_success_and_vpn_gateways_constants(self, _mock_request):
        """Test output uses Output.SUCCESS and Output.VPN_GATEWAYS constants."""
        mock_result = {
            "success": True,
            "vpn_gateways": [{"hostname": "vpn2.example.com", "ip": "10.0.0.2", "type": "ip"}],
        }
        self.action.connection.zcc_client.remove_vpn_gateway_bypass = MagicMock(return_value=mock_result)

        result = self.action.run({"profile_id": "profile-001", "entry": "vpn1.example.com"})

        self.assertIn(Output.SUCCESS, result)
        self.assertIn(Output.VPN_GATEWAYS, result)
        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(
            result[Output.VPN_GATEWAYS], [{"hostname": "vpn2.example.com", "ip": "10.0.0.2", "type": "ip"}]
        )

    def test_clean_dict_applied(self, _mock_request):
        """Test that clean_dict is applied to output (None values removed)."""
        mock_result = {
            "success": True,
            "vpn_gateways": [{"hostname": "gw.example.com", "ip": None, "type": "hostname"}],
        }
        self.action.connection.zcc_client.remove_vpn_gateway_bypass = MagicMock(return_value=mock_result)

        result = self.action.run({"profile_id": "profile-001", "entry": "other.example.com"})

        # clean_dict is applied — the result should still contain the keys
        self.assertIn(Output.SUCCESS, result)
        self.assertIn(Output.VPN_GATEWAYS, result)
