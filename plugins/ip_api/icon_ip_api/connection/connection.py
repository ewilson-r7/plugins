import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import ConnectionTestException

from icon_ip_api.connection.schema import ConnectionSchema, Input
from icon_ip_api.util.api import ApiClient


class Connection(insightconnect_plugin_runtime.Connection):
    def __init__(self):
        super().__init__(input=ConnectionSchema())
        self.client = None

    def connect(self, params: dict = None) -> None:
        self.logger.info("Establishing connection to ip-api.com (no credentials required).")
        self.client = ApiClient(logger=self.logger)

    def test(self) -> dict:
        try:
            self.client.test_connection()
        except Exception as error:
            raise ConnectionTestException(
                cause="Connection test to ip-api.com failed.",
                assistance="Verify network connectivity and that ip-api.com is reachable.",
                data=str(error),
            ) from error
        return {"success": True}
