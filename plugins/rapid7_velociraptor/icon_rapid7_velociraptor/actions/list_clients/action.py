import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import ListClientsInput, ListClientsOutput, Input, Output, Component


class ListClients(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="list_clients", description=Component.DESCRIPTION, input=ListClientsInput(), output=ListClientsOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        hostname = params.get(Input.HOSTNAME)
        os_filter = params.get(Input.OS)
        label = params.get(Input.LABEL)
        status = params.get(Input.STATUS, "ALL")
        limit = params.get(Input.LIMIT, 100)
        # END INPUT BINDING - DO NOT REMOVE

        response = self.connection.client.list_clients(
            hostname=hostname,
            os_filter=os_filter,
            label=label,
            status=status,
            limit=limit,
        )

        clients = response.get("data", []) if isinstance(response, dict) else response

        return clean(
            {
                Output.CLIENTS: clients,
                Output.COUNT: len(clients) if clients else 0,
            }
        )
