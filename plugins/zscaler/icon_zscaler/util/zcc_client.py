import ipaddress
import json
import re

from icon_zscaler.util.base_client import BaseClient

JSON_HEADERS = {"Content-Type": "application/json", "Cache-Control": "no-cache"}


def _is_ip_value(value: str) -> bool:
    """Return True if the value is an IP address or CIDR range."""
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        pass
    try:
        ipaddress.ip_network(value, strict=False)
        return True
    except ValueError:
        return False


def normalize_gateway_entry(entry: object) -> dict:
    """Normalize a VPN gateway bypass entry into hostname, ip and type fields.

    Zscaler returns vpnGateways entries as plain strings in some tenants and as
    objects in others, so both shapes are handled. For string entries the type is
    inferred by testing whether the value parses as an IP address or CIDR range.

    Args:
        entry: A single vpnGateways element, either a dict or a string.

    Returns:
        Dict with hostname, ip and type keys.
    """
    if isinstance(entry, dict):
        return {
            "hostname": entry.get("hostname", ""),
            "ip": entry.get("ip", ""),
            "type": entry.get("type", ""),
        }

    value = str(entry).strip()
    if _is_ip_value(value):
        return {"hostname": "", "ip": value, "type": "ip"}
    return {"hostname": value, "ip": "", "type": "hostname"}


def normalize_profile_id(value: object) -> str:
    """Render a profile ID as a plain string without a trailing decimal.

    Zscaler returns profileId as a JSON number, so an ID of 14729 deserializes to the
    float 14729.0 and str() would produce 14729.0. That value is not usable in a
    request path, so whole numbers are rendered without the decimal portion.

    Args:
        value: The profileId or id value from an application profile.

    Returns:
        The profile ID as a string.
    """
    if isinstance(value, bool):
        return str(value)

    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    text = str(value).strip()
    if re.fullmatch(r"\d+\.0+", text):
        return text.split(".", 1)[0]
    return text


def extract_gateway_entries(policy_extension: dict) -> tuple:
    """Pull the vpnGateways entries out of a profile's policyExtension.

    Tenants return vpnGateways either as a comma separated string or as a list.
    Iterating a string directly would walk it character by character, so the string
    form is split into entries first.

    Args:
        policy_extension: The policyExtension object from an application profile.

    Returns:
        Tuple of (entries, was_string) where entries is a list of the raw entries in
        their original form and was_string records whether the source was a string,
        so an update can be written back in the same shape.
    """
    raw_gateways = policy_extension.get("vpnGateways")

    if not raw_gateways:
        return [], False

    if isinstance(raw_gateways, str):
        return [part.strip() for part in raw_gateways.split(",") if part.strip()], True

    if isinstance(raw_gateways, list):
        return raw_gateways, False

    return [], False


class ZCCClient(BaseClient):
    """ZCC (Zscaler Client Connector) client for OneAPI.

    Handles ZCC-specific API operations including VPN gateway bypass auditing
    and management via the /zcc/papi/public/v1 service prefix.
    """

    def __init__(
        self,
        client_id: str,
        private_key: str,
        vanity_domain: str,
        cloud: str,
        logger: object,
        token_provider: object = None,
    ):
        super().__init__(client_id, private_key, vanity_domain, cloud, logger, token_provider)
        self.service_prefix = "/zcc/papi/public/v1"

    def get_vpn_gateway_bypasses(self, profile_id: str = None) -> list:
        """Get VPN gateway bypass entries from application profiles.

        Args:
            profile_id: Optional profile ID to filter results to a single profile.

        Returns:
            List of dicts keyed to match the vpn_gateway_profile output type:
            [{"profile_id": str, "profile_name": str, "vpn_gateways": [{"hostname": str, "ip": str, "type": str}]}]
        """
        response = self._make_request("GET", "web/policy/listByCompany")
        profiles_data = response.json()

        results = []
        # Handle both list responses and dict responses with a list field
        profiles = profiles_data if isinstance(profiles_data, list) else profiles_data.get("profiles", [])

        normalized_id = normalize_profile_id(profile_id) if profile_id else None

        for profile in profiles:
            current_id = normalize_profile_id(profile.get("profileId", profile.get("id", "")))

            # Skip non-matching profiles when filtering by ID
            if normalized_id and current_id != normalized_id:
                continue

            policy_extension = profile.get("policyExtension")
            if not policy_extension:
                continue

            raw_entries, _ = extract_gateway_entries(policy_extension)
            if not raw_entries:
                continue

            results.append(
                {
                    "profile_id": current_id,
                    "profile_name": profile.get("profileName", profile.get("name", "")),
                    "vpn_gateways": [normalize_gateway_entry(entry) for entry in raw_entries],
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

        # Normalize both sides so a value of either 14729 or 14729.0 is accepted
        target_id = normalize_profile_id(profile_id)

        # Find the target profile
        target_profile = None
        for profile in profiles:
            if normalize_profile_id(profile.get("profileId", profile.get("id", ""))) == target_id:
                target_profile = profile
                break

        # If profile not found or has no policyExtension/vpnGateways, return success (idempotent)
        if not target_profile:
            return {"success": True, "vpn_gateways": []}

        policy_extension = target_profile.get("policyExtension")
        if not policy_extension:
            return {"success": True, "vpn_gateways": []}

        current_gateways, was_string = extract_gateway_entries(policy_extension)
        if not current_gateways:
            return {"success": True, "vpn_gateways": []}

        # Filter in the entries' original form so the PATCH preserves the tenant's shape
        remaining = [gateway for gateway in current_gateways if not self._matches_gateway(gateway, entry_to_remove)]

        # Write back in the same shape the tenant uses, joining if it was a string
        patch_value = ",".join(remaining) if was_string else remaining
        self._make_request(
            "PATCH",
            f"application-profiles/{target_id}",
            data=json.dumps({"vpnGateways": patch_value}),
            headers=JSON_HEADERS.copy(),
        )

        # Return normalized objects to match the vpn_gateway_entry output type
        return {"success": True, "vpn_gateways": [normalize_gateway_entry(entry) for entry in remaining]}

    @staticmethod
    def _matches_gateway(gateway: object, target: str) -> bool:
        """Return True if a gateway entry matches the target hostname or IP.

        Args:
            gateway: A single vpnGateways element, either a dict or a string.
            target: The hostname or IP to match against.

        Returns:
            True if the entry should be treated as the removal target.
        """
        if not target:
            return False

        normalized = normalize_gateway_entry(gateway)
        return target in (value for value in (normalized["hostname"], normalized["ip"]) if value)

    def test(self) -> dict:
        """Test connectivity to the ZCC API.

        Calls GET web/policy/listByCompany to validate ZCC connectivity.

        Returns:
            Dict with success status: {"success": True}
        """
        self._make_request("GET", "web/policy/listByCompany")
        return {"success": True}
