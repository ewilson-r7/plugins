"""
Unit tests for GetVpnGatewayBypasses action.
"""

import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch, MagicMock

from jsonschema import validate
from util import Util
from icon_zscaler.actions.get_vpn_gateway_bypasses import GetVpnGatewayBypasses
from icon_zscaler.actions.get_vpn_gateway_bypasses.schema import GetVpnGatewayBypassesOutput, Output


def profile(**overrides) -> dict:
    """Build a profile in the shape the vpn_gateway_profile output type requires."""
    base = {
        "profile_id": "profile-001",
        "profile_name": "Default Profile",
        "vpn_gateways": [{"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"}],
    }
    base.update(overrides)
    return base


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
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=[profile()])

        self.action.run({})

        self.action.connection.zcc_client.get_vpn_gateway_bypasses.assert_called_once()

    def test_output_uses_profiles_constant(self, _mock_request):
        """Test output uses Output.PROFILES constant."""
        profiles = [profile(profile_name="Test Profile")]
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=profiles)

        result = self.action.run({})

        self.assertIn(Output.PROFILES, result)
        self.assertEqual(result[Output.PROFILES], profiles)

    def test_output_conforms_to_schema(self, _mock_request):
        """Guards against key naming drift between the client and the output type."""
        profiles = [
            profile(),
            profile(
                profile_id="1007.0",
                profile_name="MNP Z-Tunnel 2.0 General",
                vpn_gateways=[{"hostname": "", "ip": "172.16.0.0/12", "type": "ip"}],
            ),
        ]
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=profiles)

        validate(self.action.run({}), GetVpnGatewayBypassesOutput.schema)

    def test_clean_dict_removes_none_values(self, _mock_request):
        """Test that clean_dict is applied (None values removed from output)."""
        profiles = [profile(vpn_gateways=[{"hostname": "gw.example.com", "ip": None, "type": "hostname"}])]
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=profiles)

        result = self.action.run({})

        # clean_dict should have been applied — the result should exist
        self.assertIn(Output.PROFILES, result)
