import ipaddress
import re

from insightconnect_plugin_runtime.exceptions import PluginException

from icon_fortinet_fortimanager.util.constants import ADDRESS_FIELD_ALIASES, ADDRESS_TYPE_BY_ID

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
    def collapse_scalar(value) -> str:
        """Collapse a FortiManager field value into a single trimmed string.

        FortiManager frequently returns single-valued fields wrapped in a list.
        Lists are space-joined, everything else is stringified.

        Args:
            value: A raw value from a FortiManager JSON-RPC response.

        Returns:
            The value as a trimmed string, or '' when empty/None.
        """
        if value is None:
            return ""
        if isinstance(value, list):
            return " ".join(str(item) for item in value if item not in (None, "")).strip()
        return str(value).strip()

    @staticmethod
    def normalize_subnet(value) -> str:
        """Normalize a FortiManager subnet value to CIDR notation.

        FortiManager returns subnet as a two-element list of address and netmask
        (e.g. ['198.51.100.100', '255.255.255.255']). Falls back to the raw string
        when the value cannot be parsed as a network.

        Args:
            value: The raw subnet value (list, string, or None).

        Returns:
            The subnet in CIDR notation, or '' when empty.
        """
        raw = Helpers.collapse_scalar(value)
        if not raw:
            return ""
        network = Helpers._parse_subnet(raw.lower())
        return str(network) if network is not None else raw

    @staticmethod
    def normalize_address_type(raw_type, address_object: dict = None) -> str:
        """Normalize the address `type` field to the string name the schema declares.

        FortiManager returns this field as an integer on read but accepts the string
        name on write. Known IDs are mapped; an unmapped integer is rendered as its
        numeric string rather than guessed at, so the value is never mislabelled and
        never fails schema validation. When the field is absent entirely, the type is
        inferred from whichever value field the API did return.

        Args:
            raw_type: The raw `type` value from the API response.
            address_object: The full object, used to infer an absent type.

        Returns:
            The address type as a string.
        """
        if isinstance(raw_type, str) and raw_type.strip():
            return raw_type.strip()
        if isinstance(raw_type, bool):
            return str(raw_type)
        if isinstance(raw_type, int):
            return ADDRESS_TYPE_BY_ID.get(raw_type, str(raw_type))
        return Helpers._infer_address_type(address_object or {})

    @staticmethod
    def _infer_address_type(address_object: dict) -> str:
        """Infer an address type from the value fields present in the object."""
        if Helpers.collapse_scalar(address_object.get("subnet")):
            return "ipmask"
        if Helpers.collapse_scalar(address_object.get("fqdn")):
            return "fqdn"
        start_ip = address_object.get("start-ip") or address_object.get("start_ip")
        if Helpers.collapse_scalar(start_ip):
            return "iprange"
        return ""

    @staticmethod
    def normalize_address_object(address_object: dict) -> dict:
        """Coerce a FortiManager address object into the plugin's declared schema.

        FortiManager's JSON-RPC returns loosely typed values: `subnet` arrives as a
        list, `type` as an integer, and several fields use hyphenated names that the
        underscored schema never matched. Emitting only the declared fields means an
        unexpected or newly added API field can never fail output validation.

        `name` and `type` are always present because the address_object type marks
        them required.

        Args:
            address_object: A raw address object dict from the API.

        Returns:
            A dict conforming to the address_object schema type.
        """
        if not isinstance(address_object, dict):
            return {"name": "", "type": ""}

        normalized = {
            "name": Helpers.collapse_scalar(address_object.get("name")),
            "type": Helpers.normalize_address_type(address_object.get("type"), address_object),
        }

        subnet = Helpers.normalize_subnet(address_object.get("subnet"))
        if subnet:
            normalized["subnet"] = subnet

        for schema_field, api_names in ADDRESS_FIELD_ALIASES.items():
            for api_name in api_names:
                value = Helpers.collapse_scalar(address_object.get(api_name))
                if value:
                    normalized[schema_field] = value
                    break

        for field in ("fqdn", "comment"):
            value = Helpers.collapse_scalar(address_object.get(field))
            if value:
                normalized[field] = value

        return normalized

    @staticmethod
    def extract_group_members(group_data: dict) -> list:
        """Extract member address object names from an address group response.

        FortiManager returns group members as a list of names, a list of objects with
        a `name` key, or a bare string for a single member.

        Args:
            group_data: The address group dict from the API.

        Returns:
            List of member address object names.
        """
        members = (group_data or {}).get("member", [])
        if isinstance(members, str):
            members = [members]
        if not isinstance(members, list):
            return []

        names = []
        for member in members:
            name = member.get("name", "") if isinstance(member, dict) else Helpers.collapse_scalar(member)
            if name:
                names.append(name)
        return names

    @staticmethod
    def address_value_matches(normalized_object: dict, address: str) -> bool:
        """Check whether a normalized address object's stored value matches an address.

        Compares subnets as networks so equivalent notations match (a bare IP, its /32
        CIDR form, and FortiManager's address+netmask form are all treated as equal).
        FQDN and IP range endpoints are compared case-insensitively.

        Args:
            normalized_object: An object already passed through normalize_address_object.
            address: The address value to look for.

        Returns:
            True if the object's stored value represents the given address.
        """
        needle = (address or "").strip().lower()
        if not needle:
            return False

        subnet = normalized_object.get("subnet", "")
        if subnet and Helpers._subnet_matches(subnet.lower(), needle):
            return True

        fqdn = normalized_object.get("fqdn", "")
        if fqdn and fqdn.lower() == needle:
            return True

        start_ip = normalized_object.get("start_ip", "").lower()
        end_ip = normalized_object.get("end_ip", "").lower()
        if start_ip and needle in (start_ip, end_ip):
            return True

        return False

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
        """Apply case-insensitive filters with AND logic.

        Each filter key maps to an object field. Returns objects where ALL
        filter values match the corresponding field (case-insensitive).
        Handles special cases:
        - List fields (e.g. subnet as ["ip", "mask"]): joined with space for comparison
        - Subnet filter: compares both CIDR and space-separated formats

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
                # Handle list values (FortiManager returns subnet as list: ["ip", "mask"])
                if isinstance(obj_value, list):
                    obj_value = " ".join(str(item) for item in obj_value)
                obj_str = str(obj_value).lower().strip()
                filter_str = str(value).lower().strip()
                # For subnet field, also try CIDR-to-netmask comparison
                if key == "subnet" and not Helpers._subnet_matches(obj_str, filter_str):
                    match = False
                    break
                if key != "subnet" and obj_str != filter_str:
                    match = False
                    break
            if match:
                result.append(obj)

        return result

    @staticmethod
    def _subnet_matches(obj_subnet: str, filter_subnet: str) -> bool:
        """Compare subnet values accounting for different formats.

        Handles:
        - Exact string match
        - FortiManager format "ip mask" vs CIDR "ip/prefix"
        - Both normalized to ip_network for comparison

        Args:
            obj_subnet: The subnet value from the object (lowercased).
            filter_subnet: The filter value (lowercased).

        Returns:
            True if the subnets represent the same network.
        """
        # Direct string match
        if obj_subnet == filter_subnet:
            return True

        # Try normalizing both to ip_network and compare
        try:
            # Handle FortiManager "ip mask" format (e.g. "10.0.0.1 255.255.255.255")
            obj_network = Helpers._parse_subnet(obj_subnet)
            filter_network = Helpers._parse_subnet(filter_subnet)
            if obj_network is not None and filter_network is not None:
                return obj_network == filter_network
        except (ValueError, TypeError):
            pass

        return False

    @staticmethod
    def _parse_subnet(value: str):
        """Parse a subnet string in either CIDR or 'ip mask' format to ip_network.

        Args:
            value: Subnet string like "10.0.0.1/32" or "10.0.0.1 255.255.255.255"

        Returns:
            ipaddress.IPv4Network or None if unparseable.
        """
        value = value.strip()

        # Try CIDR format first
        if "/" in value:
            try:
                return ipaddress.ip_network(value, strict=False)
            except (ValueError, TypeError):
                return None

        # Try "ip mask" format (space-separated)
        parts = value.split()
        if len(parts) == 2:
            try:
                ip_addr = ipaddress.ip_address(parts[0])
                mask = ipaddress.ip_address(parts[1])
                # Convert netmask to prefix length
                prefix_len = ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
                return ipaddress.ip_network(f"{ip_addr}/{prefix_len}", strict=False)
            except (ValueError, TypeError):
                return None

        # Try bare IP (treat as /32)
        try:
            ipaddress.ip_address(value)
            return ipaddress.ip_network(f"{value}/32", strict=False)
        except (ValueError, TypeError):
            return None

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
