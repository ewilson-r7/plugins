import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import (
    GetTenantAllowBlockListItemsInput,
    GetTenantAllowBlockListItemsOutput,
    Input,
    Output,
    Component,
)

# Custom imports below
from ...util.utils import Utils


class GetTenantAllowBlockListItems(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="get_tenant_allow_block_list_items",
            description=Component.DESCRIPTION,
            input=GetTenantAllowBlockListItemsInput(),
            output=GetTenantAllowBlockListItemsOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        action_type = params.get(Input.ACTION_TYPE, "")
        list_type = params.get(Input.LIST_TYPE)
        # END INPUT BINDING - DO NOT REMOVE

        out, error = self.connection.client.get_tenant_allow_block_list_items(
            list_type=list_type,
            action_type=action_type if action_type else None,
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
                cause="PowerShell returned an error while retrieving Tenant Allow/Block List items.",
                assistance="Please verify your credentials have the Tenant AllowBlockList Manager role.",
                data=error,
            )

        entries = Utils.load_json(Utils.extract_data(out), self.logger)

        return {Output.ENTRIES: entries if entries else []}
