import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException

from icon_ip_api.actions.geolocate_bulk.schema import (
    Component,
    GeolocateBulkInput,
    GeolocateBulkOutput,
    Input,
    Output,
)

MAX_BULK_QUERIES = 100


class GeolocateBulk(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super().__init__(
            name="geolocate_bulk",
            description=Component.DESCRIPTION,
            input=GeolocateBulkInput(),
            output=GeolocateBulkOutput(),
        )

    def run(self, params: dict = None) -> dict:
        if params is None:
            params = {}

        queries = params.get(Input.QUERIES, [])
        lang = params.get(Input.LANG, "en") or "en"

        self.logger.info(f"Running geolocate_bulk action for {len(queries)} queries, lang: {lang}")

        if len(queries) > MAX_BULK_QUERIES:
            raise PluginException(
                cause=f"Too many queries submitted: {len(queries)}.",
                assistance=f"Reduce the number of queries to {MAX_BULK_QUERIES} or fewer.",
            )

        results = self.connection.client.geolocate_bulk(queries, lang)
        return {Output.RESULTS: results}
