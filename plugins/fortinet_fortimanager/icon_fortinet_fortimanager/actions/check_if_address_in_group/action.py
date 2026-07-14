import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import CheckIfAddressInGroupInput, CheckIfAddressInGroupOutput, Input, Output, Component

# Custom imports below


class CheckIfAddressInGroup(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
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
        enable_search = params.get(Input.ENABLE_SEARCH)
        group = params.get(Input.GROUP)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: use input override or fall back to connection default
        adom = adom or self.connection.default_adom

        # Fetch group — API raises PluginException if group not found
        group_data = self.connection.api.get_address_group(adom, group)

        # Extract member names from the group
        members = group_data.get("member", [])
        if isinstance(members, list):
            member_names = [m if isinstance(m, str) else m.get("name", "") for m in members]
        else:
            member_names = []

        if not enable_search:
            # Name-based match: exact match of address input against member object names
            matching = [name for name in member_names if name == address]
        else:
            # Value-based search: compare input against stored subnet/FQDN of each member
            all_objects = self.connection.api.get_address_objects(adom)

            # Build lookup of address objects by name
            obj_lookup = {obj.get("name", ""): obj for obj in all_objects}

            matching = []
            for member_name in member_names:
                obj = obj_lookup.get(member_name, {})
                # Check subnet value
                subnet = obj.get("subnet", "")
                if subnet and subnet.lower() == address.lower():
                    matching.append(member_name)
                    continue
                # Check FQDN value
                fqdn = obj.get("fqdn", "")
                if fqdn and fqdn.lower() == address.lower():
                    matching.append(member_name)

        return {
            Output.FOUND: len(matching) > 0,
            Output.ADDRESS_OBJECTS: matching,
        }
