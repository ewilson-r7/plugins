import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import ConnectionTestException, PluginException

from .schema import ConnectionSchema, Input
from icon_rapid7_velociraptor.util.api import VelociraptorApiClient


class Connection(insightconnect_plugin_runtime.Connection):

    def __init__(self):
        super().__init__(input=ConnectionSchema())
        self.client = None

    def connect(self, params):  # pylint: disable=signature-differs
        self.logger.info("Connect: Connecting...")
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        api_key = params.get(Input.API_KEY, {}).get("secretKey", "").strip()
        org_id = params.get(Input.ORG_ID, "").strip()
        region = params.get(Input.REGION, "").strip()
        # END INPUT BINDING - DO NOT REMOVE

        self.client = VelociraptorApiClient(
            api_key=api_key,
            region=region,
            org_id=org_id,
            logger=self.logger,
        )

    def test(self):
        try:
            self.client.test()
        except PluginException as error:
            raise ConnectionTestException(cause=error.cause, assistance=error.assistance, data=error.data) from error
        return {"success": True}
