import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.exceptions import PluginException
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import RemoveAddressObjectFromGroupInput, RemoveAddressObjectFromGroupOutput, Input, Output, Component

# Custom imports below


class RemoveAddressObjectFromGroup(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="remove_address_object_from_group",
            description=Component.DESCRIPTION,
            input=RemoveAddressObjectFromGroupInput(),
            output=RemoveAddressObjectFromGroupOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        address_object = params.get(Input.ADDRESS_OBJECT)
        adom = params.get(Input.ADOM)
        group = params.get(Input.GROUP)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: use input override or fall back to connection default
        adom = adom or self.connection.default_adom

        # Fetch current group (API raises PluginException if group not found)
        group_data = self.connection.api.get_address_group(adom, group)

        # Get current member list
        members = group_data.get("member", [])
        if isinstance(members, list):
            member_names = [m if isinstance(m, str) else m.get("name", "") for m in members]
        else:
            member_names = []

        # Verify that the address object is a member of the group
        if address_object not in member_names:
            raise PluginException(
                cause=f"Address object '{address_object}' is not a member of group '{group}'.",
                assistance="Verify the address object name and group membership.",
            )

        # Remove the address object from the member list
        member_names.remove(address_object)

        # Update the group with the new member list
        self.connection.api.update_address_group(adom, group, member_names)

        return {
            Output.SUCCESS: True,
            Output.ADDRESS_OBJECTS: member_names,
        }
