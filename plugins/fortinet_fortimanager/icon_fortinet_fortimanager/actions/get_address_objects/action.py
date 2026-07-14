import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetAddressObjectsInput, GetAddressObjectsOutput, Input, Output, Component

# Custom imports below
from icon_fortinet_fortimanager.util.helpers import Helpers


class GetAddressObjects(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="get_address_objects",
            description=Component.DESCRIPTION,
            input=GetAddressObjectsInput(),
            output=GetAddressObjectsOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        adom = params.get(Input.ADOM)
        fqdn_filter = params.get(Input.FQDN_FILTER)
        name_filter = params.get(Input.NAME_FILTER)
        subnet_filter = params.get(Input.SUBNET_FILTER)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: input override or connection default
        adom = adom or self.connection.default_adom

        # Fetch all address objects from the ADOM
        objects = self.connection.api.get_address_objects(adom)

        # Build filter dict from inputs
        filters = {
            "name": name_filter or "",
            "subnet": subnet_filter or "",
            "fqdn": fqdn_filter or "",
        }

        # Apply client-side filters with AND semantics
        filtered = Helpers.filter_objects(objects, filters)

        return {Output.ADDRESS_OBJECTS: filtered}
