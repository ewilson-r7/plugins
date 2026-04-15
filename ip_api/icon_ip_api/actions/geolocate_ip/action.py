import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException

from icon_ip_api.actions.geolocate_ip.schema import (
    Component,
    GeolocateIpInput,
    GeolocateIpOutput,
    Input,
    Output,
)


class GeolocateIp(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super().__init__(
            name="geolocate_ip",
            description=Component.DESCRIPTION,
            input=GeolocateIpInput(),
            output=GeolocateIpOutput(),
        )

    def run(self, params: dict = None) -> dict:
        if params is None:
            params = {}

        query = params.get(Input.QUERY, "")
        lang = params.get(Input.LANG, "en") or "en"

        self.logger.info(f"Running geolocate_ip action for query: {query}, lang: {lang}")

        result = self.connection.client.geolocate(query, lang)
        return {Output.RESULT: result}
