import json

import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException
from insightconnect_plugin_runtime.helper import clean
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import Component, CustomApiRequestInput, CustomApiRequestOutput, Input, Output

# Custom imports below

JSON_HEADERS = {"Content-Type": "application/json", "Cache-Control": "no-cache"}
METHODS_WITHOUT_BODY = ("GET", "DELETE")


class CustomApiRequest(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="custom_api_request",
            description=Component.DESCRIPTION,
            input=CustomApiRequestInput(),
            output=CustomApiRequestOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        body = params.get(Input.BODY)
        method = params.get(Input.METHOD, "GET")
        path = params.get(Input.PATH)
        service = params.get(Input.SERVICE)
        # END INPUT BINDING - DO NOT REMOVE

        client = self._resolve_client(service)
        method = method.upper()

        kwargs = {}
        if body and method not in METHODS_WITHOUT_BODY:
            kwargs["data"] = json.dumps(body)
            kwargs["headers"] = JSON_HEADERS.copy()

        response = client.raw_request(method, path, **kwargs)

        self.logger.info(f"Zscaler returned HTTP {response.status_code} for {response.url}")

        return clean(
            {
                Output.STATUS_CODE: response.status_code,
                Output.URL: response.url,
                Output.RESPONSE: response.text,
            }
        )

    def _resolve_client(self, service: str):
        """Map the requested service to its API client.

        Args:
            service: One of ZIA, ZPA or ZCC.

        Returns:
            The client for that service.

        Raises:
            PluginException: If the service is not recognised.
        """
        clients = {
            "ZIA": self.connection.zia_client,
            "ZPA": self.connection.zpa_client,
            "ZCC": self.connection.zcc_client,
        }

        client = clients.get(service.upper() if service else "")
        if not client:
            raise PluginException(
                cause=f"Unsupported service: {service}.",
                assistance=f"Provide one of the following services: {', '.join(clients)}.",
            )
        return client
