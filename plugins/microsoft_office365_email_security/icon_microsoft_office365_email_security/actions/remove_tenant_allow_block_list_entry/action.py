import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import (
    RemoveTenantAllowBlockListEntryInput,
    RemoveTenantAllowBlockListEntryOutput,
    Input,
    Output,
    Component,
)

# Custom imports below


class RemoveTenantAllowBlockListEntry(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="remove_tenant_allow_block_list_entry",
            description=Component.DESCRIPTION,
            input=RemoveTenantAllowBlockListEntryInput(),
            output=RemoveTenantAllowBlockListEntryOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        entries = params.get(Input.ENTRIES)
        list_type = params.get(Input.LIST_TYPE)
        # END INPUT BINDING - DO NOT REMOVE

        if not entries:
            raise PluginException(
                cause="No entries provided.",
                assistance="Please provide at least one entry to remove from the Tenant Allow/Block List.",
            )

        out, error = self.connection.client.remove_tenant_allow_block_list_entry(
            list_type=list_type,
            entries=entries,
        )

        if isinstance(error, bytes):
            error = error.decode("utf-8")
        if isinstance(out, bytes):
            out = out.decode("utf-8")

        if error and "Success" not in out:
            self.logger.error(f"Error output received: \n{error}")
            if out:
                self.logger.error(f"Standard output received: \n{out}")
            raise PluginException(
                cause="PowerShell returned an error while removing Tenant Allow/Block List entries.",
                assistance="Please verify your credentials have the Tenant AllowBlockList Manager role "
                "and that the entries exist in the specified list type.",
                data=error,
            )

        return {Output.SUCCESS: True}
