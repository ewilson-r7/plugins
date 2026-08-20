import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import CheckIfAddressInGroupInput, CheckIfAddressInGroupOutput, Input, Output, Component

# Custom imports below
from icon_fortinet_fortimanager.util.helpers import Helpers


class CheckIfAddressInGroup(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="check_if_address_in_group",
            description=Component.DESCRIPTION,
            input=CheckIfAddressInGroupInput(),
            output=CheckIfAddressInGroupOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        address = params.get(Input.ADDRESS)
        adom = params.get(Input.ADOM)
        group = params.get(Input.GROUP)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: use input override or fall back to connection default
        adom = adom or self.connection.default_adom
        address = (address or "").strip()

        # Fetch group — API raises PluginException if group not found
        group_data = self.connection.api.get_address_group(adom, group)
        member_names = Helpers.extract_group_members(group_data)

        if not member_names:
            return {
                Output.FOUND: False,
                Output.ADDRESS_OBJECTS: [],
                Output.MESSAGE: f"Address group '{group}' has no members.",
            }

        matching = self._find_matches(adom, member_names, address)

        return {
            Output.FOUND: len(matching) > 0,
            Output.ADDRESS_OBJECTS: matching,
            Output.MESSAGE: self._build_message(matching, address, group),
        }

    def _find_matches(self, adom: str, member_names: list, address: str) -> list:
        """Match the address against member object names and their stored values.

        Both are always checked: an exact (case-insensitive) name match, and the
        object's stored subnet, FQDN, or IP range value. This means the caller can
        pass either an object name or the address itself without choosing a mode.
        """
        needle = address.lower()
        matching = [name for name in member_names if name.lower() == needle]

        # Value-based match against the stored subnet/FQDN/range of each member.
        # FortiManager returns these loosely typed, so normalize before comparing.
        all_objects = self.connection.api.get_address_objects(adom)
        object_lookup = {}
        for raw_object in all_objects:
            normalized = Helpers.normalize_address_object(raw_object)
            if normalized.get("name"):
                object_lookup[normalized["name"]] = normalized

        for member_name in member_names:
            if member_name in matching:
                continue
            normalized = object_lookup.get(member_name)
            if normalized and Helpers.address_value_matches(normalized, address):
                matching.append(member_name)

        return matching

    @staticmethod
    def _build_message(matching: list, address: str, group: str) -> str:
        """Describe the lookup result for workflow troubleshooting."""
        if not matching:
            return f"No address object matching '{address}' was found in group '{group}'."
        plural = "" if len(matching) == 1 else "s"
        return (
            f"Found {len(matching)} matching address object{plural} in group '{group}': "
            f"{', '.join(matching)}."
        )
