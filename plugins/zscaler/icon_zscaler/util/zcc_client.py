import json

from icon_zscaler.util.base_client import BaseClient

JSON_HEADERS = {"Content-Type": "application/json", "Cache-Control": "no-cache"}


class ZCCClient(BaseClient):
    """ZCC (Zscaler Client Connector) client for OneAPI.

    Handles ZCC-specific API operations including VPN gateway bypass auditing
    and management via the /zcc/papi/public/v1 service prefix.
    """

    def __init__(self, client_id: str, private_key: str, vanity_domain: str, cloud: str, logger: object):
        super().__init__(client_id, private_key, vanity_domain, cloud, logger)
        self.service_prefix = "/zcc/papi/public/v1"

    def get_vpn_gateway_bypasses(self) -> list:
        """Get VPN gateway bypass entries from all application profiles.

        Calls GET web/policy/listByCompany, iterates application profiles,
        and extracts policyExtension.vpnGateways from each profile.

        Returns:
            List of dicts with structure:
            [{"profileId": str, "profileName": str, "vpnGateways": [{"hostname": str, "ip": str, "type": str}]}]
        """
        response = self._make_request("GET", "web/policy/listByCompany")
        profiles_data = response.json()

        results = []
        # Handle both list responses and dict responses with a list field
        profiles = profiles_data if isinstance(profiles_data, list) else profiles_data.get("profiles", [])

        for profile in profiles:
            policy_extension = profile.get("policyExtension")
            if not policy_extension:
                continue

            vpn_gateways = policy_extension.get("vpnGateways")
            if not vpn_gateways:
                continue

            gateway_entries = []
            for gw in vpn_gateways:
                gateway_entries.append(
                    {
                        "hostname": gw.get("hostname", ""),
                        "ip": gw.get("ip", ""),
                        "type": gw.get("type", ""),
                    }
                )

            results.append(
                {
                    "profileId": str(profile.get("profileId", profile.get("id", ""))),
                    "profileName": profile.get("profileName", profile.get("name", "")),
                    "vpnGateways": gateway_entries,
                }
            )

        return results

    def remove_vpn_gateway_bypass(self, profile_id: str, entry_to_remove: str) -> dict:
        """Remove a VPN gateway bypass entry from a profile.

        Fetches the current profile's vpnGateways list, filters out the entry
        matching entry_to_remove (by hostname or IP), and PATCHes the profile
        with the updated list.

        Args:
            profile_id: The profile ID to modify.
            entry_to_remove: The hostname or IP of the VPN gateway entry to remove.

        Returns:
            Dict with structure: {"success": True, "vpn_gateways": updated_list}
        """
        # Fetch all profiles to find the target profile
        response = self._make_request("GET", "web/policy/listByCompany")
        profiles_data = response.json()

        profiles = profiles_data if isinstance(profiles_data, list) else profiles_data.get("profiles", [])

        # Find the target profile
        target_profile = None
        for profile in profiles:
            pid = str(profile.get("profileId", profile.get("id", "")))
            if pid == profile_id:
                target_profile = profile
                break

        # If profile not found or has no policyExtension/vpnGateways, return success (idempotent)
        if not target_profile:
            return {"success": True, "vpn_gateways": []}

        policy_extension = target_profile.get("policyExtension")
        if not policy_extension:
            return {"success": True, "vpn_gateways": []}

        current_gateways = policy_extension.get("vpnGateways", [])
        if not current_gateways:
            return {"success": True, "vpn_gateways": []}

        # Filter out the entry matching entry_to_remove by hostname or IP
        updated_gateways = [
            gw
            for gw in current_gateways
            if gw.get("hostname", "") != entry_to_remove and gw.get("ip", "") != entry_to_remove
        ]

        # PATCH the profile with the updated vpnGateways list
        patch_payload = json.dumps({"vpnGateways": updated_gateways})
        self._make_request(
            "PATCH",
            f"application-profiles/{profile_id}",
            data=patch_payload,
            headers=JSON_HEADERS.copy(),
        )

        return {"success": True, "vpn_gateways": updated_gateways}

    def test(self) -> dict:
        """Test connectivity to the ZCC API.

        Calls GET web/policy/listByCompany to validate ZCC connectivity.

        Returns:
            Dict with success status: {"success": True}
        """
        self._make_request("GET", "web/policy/listByCompany")
        return {"success": True}
