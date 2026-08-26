import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.exceptions import PluginException
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import AddAddressObjectToGroupInput, AddAddressObjectToGroupOutput, Input, Output, Component

# Custom imports below
from icon_fortinet_fortimanager.util.api import FortiManagerPluginException
from icon_fortinet_fortimanager.util.helpers import Helpers


class AddAddressObjectToGroup(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
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
        member_names = Helpers.extract_group_members(group_data)

        # Idempotent: already a member means the requested end state is already true
        if address_object in member_names:
            self.logger.info("Address object '%s' is already a member of group '%s'.", address_object, group)
            return {
                Output.SUCCESS: True,
                Output.ADDRESS_OBJECTS: member_names,
                Output.MESSAGE: (
                    f"Address object '{address_object}' is already a member of group '{group}'. "
                    "No changes were made."
                ),
            }

        member_names.append(address_object)

        # Unlike the other address actions, a failure here is NOT reported through the
        # output. The requested end state - the object being in the group - was not
        # reached and cannot be, so returning success would hide a broken workflow
        # (for example a block list that never received the address).
        try:
            self.connection.api.update_address_group(adom, group, member_names)
        except FortiManagerPluginException as error:
            if error.referenced_object_not_exist:
                raise PluginException(
                    cause=(
                        f"Address object '{address_object}' does not exist in ADOM '{adom}', "
                        f"so it cannot be added to group '{group}'."
                    ),
                    assistance=(
                        "Create the address object first with the Create Address Object action, then retry. "
                        "If a Create Address Object step ran before this one, check its Success output - "
                        "creation is skipped when the address is whitelisted or is an RFC 1918 private address."
                    ),
                    data=error.data,
                ) from error
            raise

        total = len(member_names)
        plural = "" if total == 1 else "s"
        return {
            Output.SUCCESS: True,
            Output.ADDRESS_OBJECTS: member_names,
            Output.MESSAGE: (
                f"Address object '{address_object}' added to group '{group}'. {total} member{plural} total."
            ),
        }
