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
from icon_zscaler.actions.get_vpn_gateway_bypasses.schema import (
    GetVpnGatewayBypassesOutput,
    Input,
    Output,
)


def profile(**overrides) -> dict:
    """Build a profile in the shape the vpn_gateway_profile output type requires."""
    base = {
        "profile_id": "profile-001",
        "profile_name": "Default Profile",
        "vpn_gateways": [{"hostname": "vpn1.example.com", "ip": "10.0.0.1", "type": "hostname"}],
    }
    base.update(overrides)
    return base


MULTI_PROFILES = [
    profile(profile_id="14729", profile_name="Stepan Test"),
    profile(profile_id="10649", profile_name="MNP Z-Tunnel 2.0 Canada Proxy"),
    profile(profile_id="19253", profile_name="MNP Z-Tunnel 2.0 Disableable"),
    profile(profile_id="1007", profile_name="MNP Z-Tunnel 2.0 General"),
]


@patch("requests.request", side_effect=Util.mock_request)
class TestGetVpnGatewayBypassesAction(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.action = Util.default_connector(GetVpnGatewayBypasses())
        cls.action.connection.zcc_client._token = "mock-access-token-12345"
        cls.action.connection.zcc_client._token_expiry = 9999999999

    # ------------------------------------------------------------------
    # No inputs (existing behavior)
    # ------------------------------------------------------------------

    def test_returns_all_profiles_when_no_inputs(self, _mock_request) -> None:
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=MULTI_PROFILES)

        result = self.action.run({})

        self.action.connection.zcc_client.get_vpn_gateway_bypasses.assert_called_once_with(profile_id=None)
        self.assertEqual(len(result[Output.PROFILES]), 4)

    def test_output_conforms_to_schema(self, _mock_request) -> None:
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=MULTI_PROFILES)

        validate(self.action.run({}), GetVpnGatewayBypassesOutput.schema)

    # ------------------------------------------------------------------
    # Profile ID input (server-side single-profile fetch)
    # ------------------------------------------------------------------

    def test_passes_profile_id_to_client(self, _mock_request) -> None:
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(
            return_value=[profile(profile_id="14729", profile_name="Stepan Test")]
        )

        result = self.action.run({Input.PROFILE_ID: "14729"})

        self.action.connection.zcc_client.get_vpn_gateway_bypasses.assert_called_once_with(profile_id="14729")
        self.assertEqual(len(result[Output.PROFILES]), 1)
        self.assertEqual(result[Output.PROFILES][0]["profile_id"], "14729")

    def test_profile_id_skips_search_filter(self, _mock_request) -> None:
        """When profile_id is provided, search is ignored — the API already narrows to one profile."""
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(
            return_value=[profile(profile_id="14729", profile_name="Stepan Test")]
        )

        result = self.action.run({Input.PROFILE_ID: "14729", Input.SEARCH: "nonexistent"})

        # Result still contains the profile even though search wouldn't match its name
        self.assertEqual(len(result[Output.PROFILES]), 1)

    # ------------------------------------------------------------------
    # Search input (client-side name filter)
    # ------------------------------------------------------------------

    def test_search_filters_by_profile_name(self, _mock_request) -> None:
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=MULTI_PROFILES)

        result = self.action.run({Input.SEARCH: "Z-Tunnel 2.0"})

        # "Stepan Test" should be excluded
        self.action.connection.zcc_client.get_vpn_gateway_bypasses.assert_called_once_with(profile_id=None)
        self.assertEqual(len(result[Output.PROFILES]), 3)
        names = [p["profile_name"] for p in result[Output.PROFILES]]
        self.assertNotIn("Stepan Test", names)

    def test_search_is_case_insensitive(self, _mock_request) -> None:
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=MULTI_PROFILES)

        result = self.action.run({Input.SEARCH: "stepan"})

        self.assertEqual(len(result[Output.PROFILES]), 1)
        self.assertEqual(result[Output.PROFILES][0]["profile_name"], "Stepan Test")

    def test_search_no_match_returns_empty(self, _mock_request) -> None:
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=MULTI_PROFILES)

        result = self.action.run({Input.SEARCH: "nonexistent"})

        # clean_dict removes empty lists, so profiles key may be absent
        self.assertEqual(result.get(Output.PROFILES, []), [])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def test_clean_dict_removes_none_values(self, _mock_request) -> None:
        profiles = [profile(vpn_gateways=[{"hostname": "gw.example.com", "ip": None, "type": "hostname"}])]
        self.action.connection.zcc_client.get_vpn_gateway_bypasses = MagicMock(return_value=profiles)

        result = self.action.run({})

        self.assertIn(Output.PROFILES, result)
