import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import CreateAddressObjectInput, CreateAddressObjectOutput, Input, Output, Component

# Custom imports below
from icon_fortinet_fortimanager.util.api import FortiManagerPluginException
from icon_fortinet_fortimanager.util.helpers import Helpers


class CreateAddressObject(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="create_address_object",
            description=Component.DESCRIPTION,
            input=CreateAddressObjectInput(),
            output=CreateAddressObjectOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        address = params.get(Input.ADDRESS)
        address_object_name = params.get(Input.ADDRESS_OBJECT_NAME)
        adom = params.get(Input.ADOM)
        comment = params.get(Input.COMMENT, "")
        skip_rfc1918 = params.get(Input.SKIP_RFC1918)
        whitelist = params.get(Input.WHITELIST)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: use input override or connection default
        adom = adom or self.connection.default_adom

        # Use explicit name if provided, otherwise use address value
        object_name = address_object_name or address

        # Normalize optional inputs
        whitelist = whitelist or []

        # Detect address type
        address_type = Helpers.determine_address_type(address)

        # Check whitelist — skip when matched
        if whitelist and Helpers.matches_whitelist(address, whitelist):
            self.logger.info("Address %s matches whitelist, skipping creation.", address)
            return self._skipped(f"Address '{address}' matches the whitelist. No address object was created.")

        # Check RFC 1918 if skip_rfc1918 enabled — skip when private
        if address_type == "ipmask" and skip_rfc1918 and Helpers.is_rfc1918(address):
            self.logger.info("Address %s is RFC 1918 private, skipping creation.", address)
            return self._skipped(
                f"Address '{address}' is an RFC 1918 private address and Skip RFC 1918 is enabled. "
                "No address object was created."
            )

        # Normalize IP (bare IP → /32 CIDR)
        value = address
        if address_type == "ipmask":
            value = Helpers.normalize_ip(address)

        # Create the object. An existing object is reported through the output rather
        # than failing the step, so the action is safe to re-run in a workflow.
        try:
            self.connection.api.create_address_object(adom, object_name, address_type, value, comment=comment)
        except FortiManagerPluginException as error:
            if error.object_already_exists:
                self.logger.info("Address object '%s' already exists, skipping creation.", object_name)
                return self._skipped(
                    f"Address object '{object_name}' already exists in ADOM '{adom}'. No changes were made."
                )
            raise

        created_object = {"name": object_name, "type": address_type}
        if address_type == "ipmask":
            created_object["subnet"] = value
        elif address_type == "fqdn":
            created_object["fqdn"] = value
        if comment:
            created_object["comment"] = comment

        return {
            Output.SUCCESS: True,
            Output.ADDRESS_OBJECT: created_object,
            Output.MESSAGE: f"Address object '{object_name}' created successfully in ADOM '{adom}'.",
        }

    @staticmethod
    def _skipped(message: str) -> dict:
        """Build a no-op result.

        The address_object key is omitted entirely rather than set to an empty dict:
        the address_object type marks name and type required, so an empty dict fails
        output schema validation.
        """
        return {Output.SUCCESS: False, Output.MESSAGE: message}
