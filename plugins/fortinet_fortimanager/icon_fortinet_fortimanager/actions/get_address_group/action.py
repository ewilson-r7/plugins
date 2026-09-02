import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetAddressGroupInput, GetAddressGroupOutput, Input, Output, Component

# Custom imports below
from icon_fortinet_fortimanager.util.helpers import Helpers


class GetAddressGroup(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="get_address_group",
            description=Component.DESCRIPTION,
            input=GetAddressGroupInput(),
            output=GetAddressGroupOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        adom = params.get(Input.ADOM)
        group = params.get(Input.GROUP)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: input override or connection default
        adom = adom or self.connection.default_adom

        # Fetch the group — API raises PluginException if the group does not exist
        group_data = self.connection.api.get_address_group(adom, group)

        # Normalize so a member list of objects, or a comment returned as a list,
        # cannot fail output schema validation
        address_group = Helpers.normalize_address_group(group_data)

        member_count = len(address_group["member"])
        plural = "" if member_count == 1 else "s"

        return {
            Output.ADDRESS_GROUP: address_group,
            Output.MESSAGE: (f"Address group '{address_group['name'] or group}' has {member_count} member{plural}."),
        }
