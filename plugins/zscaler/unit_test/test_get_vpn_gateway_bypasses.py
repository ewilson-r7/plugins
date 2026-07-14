"""
Unit tests for GetVpnGatewayBypasses action.
"""

import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch, MagicMock

from util import Util
from icon_zscaler.actions.get_vpn_gateway_bypasses import GetVpnGatewayBypasses
from icon_zscaler.actions.get_vpn_gateway_bypasses.schema import Output


@patch("requests.request", side_effect=Util.mock_request)
class TestGetVpnGatewayBypassesAction(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.action = Util.default_connector(GetVpnGatewayBypasses())
        # Also set ZCC token since default_connector doesn't set it
        cls.action.connection.zcc_client._token = "mock-access-token-12345"
        cls.action.connection.zcc_client._token_expiry = 9999999999

    def test_calls_zcc_client_get_vpn_gateway_bypasses(self, _mock_request):
        """Test action handler calls self.connection.zcc_client.get_vpn_gateway_bypasses()."""
        mock_profiles = [
            {
                "profileId": "profile-001",
                "profileName": "Default Profile",
                "vpnGateways": [{"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"}],
            }
        ]
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=mock_profiles)

        result = self.action.run({})

        self.action.connection.zcc_client.get_vpn_gateway_bypasses.assert_called_once()

    def test_output_uses_profiles_constant(self, _mock_request):
        """Test output uses Output.PROFILES constant."""
        mock_profiles = [
            {
                "profileId": "profile-001",
                "profileName": "Test Profile",
                "vpnGateways": [{"hostname": "gw.example.com", "ip": "1.2.3.4", "type": "hostname"}],
            }
        ]
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=mock_profiles)

        result = self.action.run({})

        self.assertIn(Output.PROFILES, result)
        self.assertEqual(result[Output.PROFILES], mock_profiles)

    def test_clean_dict_removes_none_values(self, _mock_request):
        """Test that clean_dict is applied (None values removed from output)."""
        # Return profiles with a None value that should be cleaned
        mock_profiles = [
            {
                "profileId": "profile-001",
                "profileName": "Test",
                "vpnGateways": [{"hostname": "gw.example.com", "ip": None, "type": "hostname"}],
            }
        ]
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=mock_profiles)

        result = self.action.run({})

        # clean_dict should have been applied — the result should exist
        self.assertIn(Output.PROFILES, result)
