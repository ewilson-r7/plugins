import ipaddress
import re

from insightconnect_plugin_runtime.exceptions import PluginException

# RFC 1918 private address ranges (only these three, not 127/8 or 169.254/16)
_RFC1918_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]

# FQDN pattern: valid domain name with at least one dot
_FQDN_PATTERN = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*\.[A-Za-z]{2,}$")


class Helpers:
    """Pure utility functions for address handling and filtering."""

    @staticmethod
    def determine_address_type(address: str) -> str:
        """Classify address as 'ipmask', 'fqdn', or raise PluginException.

        Args:
            address: The address string to classify.

        Returns:
            'ipmask' for valid IPv4 addresses or CIDR notation.
            'fqdn' for valid domain names.

        Raises:
            PluginException: If the address does not match any recognized format.
        """
        # Check if it's a valid IPv4 address or CIDR
        try:
            if "/" in address:
                ipaddress.ip_network(address, strict=False)
            else:
                ipaddress.ip_address(address)
            return "ipmask"
        except (ValueError, TypeError):
            pass

        # Check if it's a valid FQDN
        if _FQDN_PATTERN.match(address):
            return "fqdn"

        raise PluginException(
            cause=f"Invalid address format: {address}",
            assistance="The address must be a valid IPv4 address, CIDR notation, or fully qualified domain name.",
        )

    @staticmethod
    def normalize_ip(address: str) -> str:
        """Convert bare IP to /32 CIDR, validate CIDR notation.

        Args:
            address: An IPv4 address or CIDR string.

        Returns:
            The address in CIDR notation (e.g. '192.168.1.1/32').

        Raises:
            PluginException: If the address is not valid IPv4 or CIDR.
        """
        try:
            if "/" not in address:
                address = f"{address}/32"
            # Validate and normalize
            network = ipaddress.ip_network(address, strict=False)
            return str(network)
        except (ValueError, TypeError) as e:
            raise PluginException(
                cause=f"Invalid IP address or CIDR notation: {address}",
                assistance="Provide a valid IPv4 address or CIDR notation (e.g. 192.168.1.0/24).",
                data=str(e),
            ) from e

    @staticmethod
    def is_rfc1918(address: str) -> bool:
        """Check if IP/CIDR falls within RFC 1918 private ranges.

        Checks ONLY: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16.
        Does NOT treat 127.0.0.0/8 or 169.254.0.0/16 as RFC 1918.

        Args:
            address: An IPv4 address or CIDR string.

        Returns:
            True if the address falls within any RFC 1918 range.
        """
        try:
            if "/" not in address:
                address = f"{address}/32"
            network = ipaddress.ip_network(address, strict=False)
            return any(network.subnet_of(rfc1918_net) for rfc1918_net in _RFC1918_NETWORKS)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def matches_whitelist(address: str, whitelist: list) -> bool:
        """Check whitelist: exact match for FQDN, subnet containment for IP/CIDR.

        Args:
            address: The address to check against the whitelist.
            whitelist: List of addresses (FQDN or CIDR) to check against.

        Returns:
            True if the address matches any whitelist entry.
        """
        if not whitelist:
            return False

        # Determine if the input address is an FQDN or IP/CIDR
        address_type = None
        try:
            if "/" in address:
                ipaddress.ip_network(address, strict=False)
                address_type = "ipmask"
            else:
                ipaddress.ip_address(address)
                address_type = "ipmask"
        except (ValueError, TypeError):
            pass

        if address_type is None:
            # Treat as FQDN — case-insensitive exact match
            address_lower = address.lower()
            return any(entry.lower() == address_lower for entry in whitelist)

        # IP/CIDR — check subnet containment
        if "/" not in address:
            address = f"{address}/32"
        try:
            addr_network = ipaddress.ip_network(address, strict=False)
        except (ValueError, TypeError):
            return False

        for entry in whitelist:
            try:
                whitelist_network = ipaddress.ip_network(entry, strict=False)
                if addr_network.subnet_of(whitelist_network):
                    return True
            except (ValueError, TypeError):
                # Skip non-IP whitelist entries when comparing against IP address
                continue

        return False

    @staticmethod
    def filter_objects(objects: list, filters: dict) -> list:
        """Apply case-insensitive exact-match filters with AND logic.

        Each filter key maps to an object field. Returns objects where ALL
        filter values match the corresponding field (case-insensitive).
        Objects missing a filtered field are excluded.

        Args:
            objects: List of dict objects to filter.
            filters: Dict of field_name -> value to match.

        Returns:
            Filtered list of objects matching all criteria.
        """
        if not filters:
            return list(objects)

        # Remove empty/None filter values
        active_filters = {k: v for k, v in filters.items() if v}
        if not active_filters:
            return list(objects)

        result = []
        for obj in objects:
            match = True
            for key, value in active_filters.items():
                obj_value = obj.get(key)
                if obj_value is None:
                    match = False
                    break
                if str(obj_value).lower() != str(value).lower():
                    match = False
                    break
            if match:
                result.append(obj)

        return result

    @staticmethod
    def strip_credentials(params: dict) -> dict:
        """Strip whitespace from string credential values.

        Returns a new dict with all string values stripped of leading/trailing
        whitespace. Non-string values pass through unchanged.

        Args:
            params: Dict of credential parameters.

        Returns:
            New dict with stripped string values.
        """
        return {key: value.strip() if isinstance(value, str) else value for key, value in params.items()}

    @staticmethod
    def redact_sensitive(message: str, sensitive_values: list) -> str:
        """Replace sensitive values with '****' in log messages.

        Args:
            message: The log message string.
            sensitive_values: List of sensitive strings to redact.

        Returns:
            Message with all sensitive values replaced by '****'.
        """
        for value in sensitive_values:
            if value:
                message = message.replace(value, "****")
        return message
