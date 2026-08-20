import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import ListAddressGroupsInput, ListAddressGroupsOutput, Input, Output, Component

# Custom imports below
from icon_fortinet_fortimanager.util.helpers import Helpers


class ListAddressGroups(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="list_address_groups",
            description=Component.DESCRIPTION,
            input=ListAddressGroupsInput(),
            output=ListAddressGroupsOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        adom = params.get(Input.ADOM)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: input override or connection default
        adom = adom or self.connection.default_adom

        groups = self.connection.api.get_address_groups(adom)

        # Normalize each group so loosely typed API values cannot fail output validation
        address_groups = [Helpers.normalize_address_group(group) for group in groups]

        plural = "" if len(address_groups) == 1 else "s"

        return {
            Output.ADDRESS_GROUPS: address_groups,
            Output.MESSAGE: f"Retrieved {len(address_groups)} address group{plural} from ADOM '{adom}'.",
        }
