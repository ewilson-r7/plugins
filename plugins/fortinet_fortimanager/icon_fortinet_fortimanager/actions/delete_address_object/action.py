import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import DeleteAddressObjectInput, DeleteAddressObjectOutput, Input, Output, Component

# Custom imports below


class DeleteAddressObject(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="delete_address_object",
            description=Component.DESCRIPTION,
            input=DeleteAddressObjectInput(),
            output=DeleteAddressObjectOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        address_object = params.get(Input.ADDRESS_OBJECT)
        adom = params.get(Input.ADOM)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: input override or connection default
        adom = adom or self.connection.default_adom

        # Delete the address object — API client raises PluginException
        # for not found (error -3) and reference conflicts
        self.connection.api.delete_address_object(adom, address_object)

        return {Output.SUCCESS: True}
