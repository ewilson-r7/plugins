import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import RemoveAddressObjectFromGroupInput, RemoveAddressObjectFromGroupOutput, Input, Output, Component

# Custom imports below
from icon_fortinet_fortimanager.util.helpers import Helpers


class RemoveAddressObjectFromGroup(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
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
        member_names = Helpers.extract_group_members(group_data)

        # Not being a member is reported through the output, not raised, so a cleanup
        # workflow does not fail when the object has already been removed.
        if address_object not in member_names:
            self.logger.info(
                "Address object '%s' is not a member of group '%s', nothing to remove.",
                address_object,
                group,
            )
            return {
                Output.SUCCESS: False,
                Output.ADDRESS_OBJECTS: member_names,
                Output.MESSAGE: (
                    f"Address object '{address_object}' is not a member of group '{group}'. No changes were made."
                ),
            }

        # Remove the address object from the member list
        member_names.remove(address_object)

        # Update the group with the new member list
        self.connection.api.update_address_group(adom, group, member_names)

        remaining = len(member_names)
        plural = "" if remaining == 1 else "s"
        return {
            Output.SUCCESS: True,
            Output.ADDRESS_OBJECTS: member_names,
            Output.MESSAGE: (
                f"Address object '{address_object}' removed from group '{group}'. "
                f"{remaining} member{plural} remaining."
            ),
        }
