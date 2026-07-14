import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import AddAddressObjectToGroupInput, AddAddressObjectToGroupOutput, Input, Output, Component

# Custom imports below


class AddAddressObjectToGroup(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="add_address_object_to_group",
            description=Component.DESCRIPTION,
            input=AddAddressObjectToGroupInput(),
            output=AddAddressObjectToGroupOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        address_object = params.get(Input.ADDRESS_OBJECT)
        adom = params.get(Input.ADOM)
        group = params.get(Input.GROUP)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: input override or connection default
        adom = adom or self.connection.default_adom

        # Fetch current group — API raises PluginException if group not found (code -3)
        group_data = self.connection.api.get_address_group(adom, group)

        # Extract current member list (may be list of strings or list of dicts with "name" key)
        members = group_data.get("member", [])
        if isinstance(members, list):
            member_names = [m if isinstance(m, str) else m.get("name", "") for m in members]
        else:
            member_names = []

        # Idempotent: if address object already in group, return current list without duplicating
        if address_object in member_names:
            return {Output.SUCCESS: True, Output.ADDRESS_OBJECTS: member_names}

        # Append address object and update the group
        # API raises PluginException if address object does not exist (FortiManager rejects invalid member)
        member_names.append(address_object)
        self.connection.api.update_address_group(adom, group, member_names)

        return {Output.SUCCESS: True, Output.ADDRESS_OBJECTS: member_names}
