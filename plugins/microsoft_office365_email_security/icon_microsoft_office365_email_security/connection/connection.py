import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import ConnectionTestException
from .schema import ConnectionSchema, Input

from ..util.api import MicrosoftCommunicationAPI


class Connection(insightconnect_plugin_runtime.Connection):
    def __init__(self):
        super(self.__class__, self).__init__(input=ConnectionSchema())
        self.client = None

    def connect(self, params={}):
        self.logger.info("Connect: Connecting...")
        username = params.get(Input.CREDENTIALS).get("username")
        password = params.get(Input.CREDENTIALS).get("password")

        if "$" in password:
            self.logger.error(
                "There was a '$' in the password. This can cause issues with PowerShell Core 7. To limit potential authentication issues with this plugin, we recommend using a password that does not contain a $."
            )

        self.client = MicrosoftCommunicationAPI(username, password, self.logger)

    def test(self):
        out, err = self.client.test_connection()
        if err:
            self.logger.error("\nOutput:\n")
            self.logger.error(out.decode("utf-8"))
            self.logger.error("\nError:\n")
            self.logger.error(err.decode("utf-8"))
            raise ConnectionTestException(preset=ConnectionTestException.Preset.UNAUTHORIZED)
        self.logger.info("Connection Test Passed.")
        return {"result": True}
