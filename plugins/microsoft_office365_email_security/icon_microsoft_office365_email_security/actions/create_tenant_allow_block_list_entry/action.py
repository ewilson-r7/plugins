import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import (
    CreateTenantAllowBlockListEntryInput,
    CreateTenantAllowBlockListEntryOutput,
    Input,
    Output,
    Component,
)

# Custom imports below
from ...util.utils import Utils


class CreateTenantAllowBlockListEntry(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="create_tenant_allow_block_list_entry",
            description=Component.DESCRIPTION,
            input=CreateTenantAllowBlockListEntryInput(),
            output=CreateTenantAllowBlockListEntryOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        action_type = params.get(Input.ACTION_TYPE)
        entries = params.get(Input.ENTRIES)
        expiration_days = params.get(Input.EXPIRATION_DAYS, 30)
        list_type = params.get(Input.LIST_TYPE)
        no_expiration = params.get(Input.NO_EXPIRATION, False)
        notes = params.get(Input.NOTES, "")
        # END INPUT BINDING - DO NOT REMOVE

        if not entries:
            raise PluginException(
                cause="No entries provided.",
                assistance="Please provide at least one entry to add to the Tenant Allow/Block List.",
            )

        out, error = self.connection.client.create_tenant_allow_block_list_entry(
            list_type=list_type,
            entries=entries,
            action_type=action_type,
            no_expiration=no_expiration,
            expiration_days=expiration_days,
            notes=notes if notes else "",
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
                cause="PowerShell returned an error while creating Tenant Allow/Block List entries.",
                assistance="Please verify your credentials have the Tenant AllowBlockList Manager role "
                "and that the entries are valid for the specified list type.",
                data=error,
            )

        created_entries = Utils.load_json(Utils.extract_data(out), self.logger)

        return {
            Output.SUCCESS: True,
            Output.ENTRIES: created_entries if created_entries else [],
        }
