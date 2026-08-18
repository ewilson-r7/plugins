import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.exceptions import PluginException
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import DeleteAddressObjectInput, DeleteAddressObjectOutput, Input, Output, Component

# Custom imports below


class DeleteAddressObject(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
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

        # Delete the address object — handle not-found and in-use gracefully
        try:
            self.connection.api.delete_address_object(adom, address_object)
        except PluginException as error:
            error_cause = str(error.cause).lower()
            if "code -3" in str(error.cause) or "does not exist" in error_cause:
                self.logger.info("Address object '%s' does not exist, nothing to delete.", address_object)
                return {Output.SUCCESS: False}
            if "used by" in error_cause or "referenced" in error_cause or "cannot be deleted" in error_cause or (
                "code -10006" in str(error.cause) or "code -10015" in str(error.cause)
            ):
                raise PluginException(
                    cause=f"Cannot delete address object '{address_object}' because it is referenced by another object (e.g. an address group or policy).",
                    assistance="Remove the address object from all groups and policies before deleting it.",
                    data=error.data,
                ) from error
            raise

        return {Output.SUCCESS: True}
