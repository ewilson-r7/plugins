import requests
from insightconnect_plugin_runtime.exceptions import PluginException

from icon_rapid7_velociraptor.util.constants import BASE_URL_TEMPLATE, HTTP_ERROR_MAP, TIMEOUT


class VelociraptorApiClient:
    def __init__(self, api_key: str, region: str, org_id: str, logger):
        self._api_key = api_key
        self._region = region
        self._org_id = org_id
        self._logger = logger
        self._base_url = BASE_URL_TEMPLATE.format(region=region, org_id=org_id)

    def test(self):
        """Validate credentials by listing clients with a limit of 1."""
        self._make_request("GET", "/clients", params={"limit": 1})

    # ---- Client API ----

    def get_client(self, client_id: str) -> dict:
        return self._make_request("GET", f"/clients/{client_id}")

    def list_clients(
        self, hostname: str = None, os_filter: str = None, label: str = None, status: str = None, limit: int = None
    ) -> dict:
        params = {}
        if hostname:
            params["hostname"] = hostname
        if os_filter:
            params["os"] = os_filter
        if label:
            params["label"] = label
        if status and status != "ALL":
            params["status"] = status
        if limit:
            params["limit"] = limit
        return self._make_request("GET", "/clients", params=params)

    # ---- Label API ----

    def get_client_labels(self, client_id: str) -> list:
        return self._make_request("GET", f"/clients/{client_id}/labels")

    def add_label(self, client_id: str, label: str) -> dict:
        return self._make_request("PATCH", f"/clients/{client_id}/labels/{label}")

    def remove_label(self, client_id: str, label: str) -> None:
        self._make_request("DELETE", f"/clients/{client_id}/labels/{label}", expect_json=False)

    # ---- Flow API ----

    def create_flow(self, client_id: str, payload: dict) -> str:
        return self._make_request("POST", f"/clients/{client_id}/flows", json_data=payload)

    def get_flow(self, client_id: str, flow_id: str) -> dict:
        return self._make_request("GET", f"/clients/{client_id}/flows/{flow_id}")

    def list_flows(self, client_id: str, creator: str = None, limit: int = None) -> dict:
        params = {}
        if creator:
            params["creator"] = creator
        if limit:
            params["limit"] = limit
        return self._make_request("GET", f"/clients/{client_id}/flows", params=params)

    def get_flow_results(self, client_id: str, flow_id: str, artifact: str) -> dict:
        return self._make_request("GET", f"/clients/{client_id}/flows/{flow_id}/results/{artifact}")

    # ---- Hunt API ----

    def create_hunt(self, payload: dict) -> str:
        return self._make_request("POST", "/hunts", json_data=payload)

    def get_hunt(self, hunt_id: str) -> dict:
        return self._make_request("GET", f"/hunts/{hunt_id}")

    def list_hunts(self, state: str = None, limit: int = None) -> dict:
        params = {}
        if state:
            params["state"] = state
        if limit:
            params["limit"] = limit
        return self._make_request("GET", "/hunts", params=params)

    def get_hunt_results(self, hunt_id: str, limit: int = None) -> dict:
        params = {}
        if limit:
            params["limit"] = limit
        return self._make_request("GET", f"/hunts/{hunt_id}/results", params=params)

    # ---- Artifact API ----

    def list_artifacts(
        self,
        artifact_type: str = None,
        os_filter: str = None,
        include_built_in: bool = True,
        include_custom: bool = True,
    ) -> list:
        params = {}
        if artifact_type and artifact_type != "ALL":
            params["type"] = artifact_type
        if os_filter and os_filter != "ALL":
            params["os"] = os_filter
        if not include_built_in:
            params["includeBuiltIn"] = "false"
        if not include_custom:
            params["includeCustom"] = "false"
        return self._make_request("GET", "/artifacts", params=params)

    # ---- Internal request handling ----

    def _make_request(
        self, method: str, endpoint: str, params: dict = None, json_data: dict = None, expect_json: bool = True
    ):
        url = f"{self._base_url}{endpoint}"
        response = self._call_api(method, url, params=params, json_data=json_data)
        self._raise_for_status(response)

        if not expect_json:
            return None

        if response.status_code == 204:
            return None

        return self._parse_json(response)

    def _call_api(self, method: str, url: str, params: dict = None, json_data: dict = None):
        headers = {
            "X-Api-Key": self._api_key,
            "Accept": "application/json",
        }
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=TIMEOUT,
            )
        except requests.exceptions.Timeout as error:
            raise PluginException(preset=PluginException.Preset.TIMEOUT, data=error) from error
        except requests.exceptions.ConnectionError as error:
            raise PluginException(
                cause="Unable to connect to the Velociraptor API.",
                assistance="Verify the region is correct and the service is available.",
                data=error,
            ) from error
        return response

    def _raise_for_status(self, response):
        if response.status_code in range(200, 300):
            return
        error_info = HTTP_ERROR_MAP.get(
            response.status_code,
            {
                "cause": f"Unexpected error (HTTP {response.status_code})",
                "assistance": "Contact support if this persists.",
            },
        )
        raise PluginException(
            cause=error_info["cause"],
            assistance=error_info["assistance"],
            data=response.text,
        )

    def _parse_json(self, response):
        try:
            return response.json()
        except ValueError as error:
            raise PluginException(preset=PluginException.Preset.INVALID_JSON, data=error) from error
