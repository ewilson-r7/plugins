import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import DeleteAddressObjectInput, DeleteAddressObjectOutput, Input, Output, Component

# Custom imports below
from icon_fortinet_fortimanager.util.api import FortiManagerPluginException
from icon_fortinet_fortimanager.util.constants import ERROR_CODE_OBJECT_IN_USE, ERROR_CODE_OBJECT_NOT_EXIST


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

        # Both "already gone" and "still referenced" are reported through the output
        # rather than raised, so a workflow can branch on the result instead of failing.
        try:
            self.connection.api.delete_address_object(adom, address_object)
        except FortiManagerPluginException as error:
            if error.code == ERROR_CODE_OBJECT_NOT_EXIST:
                self.logger.info("Address object '%s' does not exist, nothing to delete.", address_object)
                return {
                    Output.SUCCESS: False,
                    Output.MESSAGE: (
                        f"Address object '{address_object}' does not exist in ADOM '{adom}'. Nothing to delete."
                    ),
                }
            if error.code == ERROR_CODE_OBJECT_IN_USE:
                self.logger.info("Address object '%s' is still referenced and cannot be deleted.", address_object)
                return {
                    Output.SUCCESS: False,
                    Output.MESSAGE: (
                        f"Address object '{address_object}' cannot be deleted because it is still in use by "
                        "another object, such as an address group or firewall policy. Remove it from those "
                        "references first, then retry the deletion."
                    ),
                }
            raise

        return {
            Output.SUCCESS: True,
            Output.MESSAGE: f"Address object '{address_object}' deleted successfully from ADOM '{adom}'.",
        }
