import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.exceptions import PluginException
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import CreateAddressObjectInput, CreateAddressObjectOutput, Input, Output, Component

# Custom imports below
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

        # Check whitelist — skip and return success=false if matched
        if whitelist and Helpers.matches_whitelist(address, whitelist):
            self.logger.info("Address %s matches whitelist, skipping creation.", address)
            return {Output.SUCCESS: False, Output.ADDRESS_OBJECT: {}}

        # Check RFC 1918 if skip_rfc1918 enabled — skip and return success=false if private
        if address_type == "ipmask" and skip_rfc1918 and Helpers.is_rfc1918(address):
            self.logger.info("Address %s is RFC 1918 private, skipping creation.", address)
            return {Output.SUCCESS: False, Output.ADDRESS_OBJECT: {}}

        # Normalize IP (bare IP → /32 CIDR)
        value = address
        if address_type == "ipmask":
            value = Helpers.normalize_ip(address)

        # Call API to create the address object — handle already-exists gracefully
        try:
            self.connection.api.create_address_object(adom, object_name, address_type, value, comment=comment)
        except PluginException as error:
            if "code -6" in str(error.cause) or "already exists" in str(error.cause).lower():
                self.logger.info("Address object '%s' already exists, skipping creation.", object_name)
                return {Output.SUCCESS: False, Output.ADDRESS_OBJECT: {}}
            raise

        # Build output object details
        created_object = {"name": object_name, "type": address_type}
        if address_type == "ipmask":
            created_object["subnet"] = value
        elif address_type == "fqdn":
            created_object["fqdn"] = value
        if comment:
            created_object["comment"] = comment

        return {Output.SUCCESS: True, Output.ADDRESS_OBJECT: created_object}
