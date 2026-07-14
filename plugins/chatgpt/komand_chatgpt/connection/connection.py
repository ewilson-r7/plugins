import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import ConnectionTestException, PluginException

from .schema import ConnectionSchema, Input
from ..util.api import ChatGPTClient


class Connection(insightconnect_plugin_runtime.Connection):

    def __init__(self):
        super(self.__class__, self).__init__(input=ConnectionSchema())
        self.client = None

    def connect(self, params):
        self.logger.info("Connect: Connecting to OpenAI API...")
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        self.api_key = params.get(Input.API_KEY)
        self.model = params.get(Input.MODEL)
        # END INPUT BINDING - DO NOT REMOVE

        api_key = self.api_key.get("secretKey", "").strip()
        model = self.model

        self.client = ChatGPTClient(
            api_key=api_key,
            model=model,
            logger=self.logger,
        )
        self.logger.info("Connect: Successfully initialized ChatGPT client with model: %s", model)

    def test(self):
        try:
            self.client.test_connection()
            return {"success": True}
        except PluginException as error:
            raise ConnectionTestException(
                cause=error.cause,
                assistance=error.assistance,
                data=error.data,
            ) from error
