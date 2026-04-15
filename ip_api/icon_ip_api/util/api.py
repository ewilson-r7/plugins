import requests
from insightconnect_plugin_runtime.exceptions import PluginException

from icon_ip_api.util.constants import BASE_URL, DEFAULT_FIELDS, TIMEOUT


class ApiClient:
    def __init__(self, logger):
        self.logger = logger
        self.session = requests.Session()

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Execute an HTTP request and return the response, raising PluginException on errors."""
        try:
            response = self.session.request(method, url, timeout=TIMEOUT, **kwargs)
        except requests.exceptions.Timeout as error:
            raise PluginException(
                preset=PluginException.Preset.TIMEOUT,
                data=str(error),
            ) from error
        except requests.exceptions.ConnectionError as error:
            raise PluginException(
                cause="A network connection error occurred while contacting ip-api.com.",
                assistance="Verify network connectivity and that ip-api.com is reachable.",
                data=str(error),
            ) from error

        self._handle_status(response)
        return response

    def _handle_status(self, response: requests.Response) -> None:
        """Inspect response status and rate-limit headers, raising PluginException as needed."""
        # Check remaining rate-limit quota before even looking at the status code.
        x_rl = response.headers.get("X-Rl")
        if x_rl == "0":
            x_ttl = response.headers.get("X-Ttl", "unknown")
            raise PluginException(
                cause="ip-api.com rate limit reached (X-Rl header is 0).",
                assistance=f"Wait {x_ttl} second(s) before retrying.",
            )

        status_code = response.status_code

        if status_code == 429:
            raise PluginException(
                preset=PluginException.Preset.RATE_LIMIT,
                cause="ip-api.com returned HTTP 429 Too Many Requests.",
                assistance="Reduce request frequency and retry after the rate-limit window resets.",
            )

        if status_code == 422:
            raise PluginException(
                preset=PluginException.Preset.BAD_REQUEST,
                cause="ip-api.com returned HTTP 422 Unprocessable Entity.",
                assistance="Ensure the batch request contains no more than 100 entries.",
            )

        if 400 <= status_code < 500:
            raise PluginException(
                preset=PluginException.Preset.BAD_REQUEST,
                cause=f"ip-api.com returned HTTP {status_code}.",
                assistance="Verify the request parameters and try again.",
                data=response.text,
            )

        if status_code >= 500:
            raise PluginException(
                preset=PluginException.Preset.SERVER_ERROR,
                cause=f"ip-api.com returned HTTP {status_code}.",
                assistance="The ip-api.com service may be temporarily unavailable. Try again later.",
                data=response.text,
            )

    def _parse_result(self, raw: dict) -> dict:
        """Rename the 'as' key to 'as_number' and strip None values."""
        result = {}
        for key, value in raw.items():
            if value is None:
                continue
            if key == "as":
                result["as_number"] = value
            else:
                result[key] = value
        return result

    def geolocate(self, query: str, lang: str = "en") -> dict:
        """Perform a single IP/domain geolocation lookup."""
        url = f"{BASE_URL}/json/{query}"
        params = {"fields": DEFAULT_FIELDS, "lang": lang}

        self.logger.info(f"Performing single geolocation lookup for: {query}")
        response = self._make_request("GET", url, params=params)

        try:
            raw = response.json()
        except ValueError as error:
            raise PluginException(
                preset=PluginException.Preset.INVALID_JSON,
                data=response.text,
            ) from error

        if raw.get("status") == "fail":
            api_message = raw.get("message", "Unknown error")
            raise PluginException(
                cause=f"ip-api.com returned a failure status: {api_message}",
                assistance="Verify the IP address or domain name is valid and publicly routable.",
                data=raw,
            )

        return self._parse_result(raw)

    def geolocate_bulk(self, queries: list, lang: str = "en") -> list:
        """Perform a batch IP/domain geolocation lookup for up to 100 entries."""
        url = f"{BASE_URL}/batch"
        params = {"fields": DEFAULT_FIELDS, "lang": lang}
        body = [{"query": q} for q in queries]

        self.logger.info(f"Performing bulk geolocation lookup for {len(queries)} queries.")
        response = self._make_request("POST", url, params=params, json=body)

        try:
            raw_list = response.json()
        except ValueError as error:
            raise PluginException(
                preset=PluginException.Preset.INVALID_JSON,
                data=response.text,
            ) from error

        results = []
        for raw in raw_list:
            # Individual fail entries are included in results rather than raising,
            # so the caller can inspect partial failures.
            results.append(self._parse_result(raw))

        return results

    def test_connection(self) -> None:
        """Validate connectivity by resolving a well-known public IP."""
        self.logger.info("Testing connection to ip-api.com by resolving 8.8.8.8.")
        self.geolocate("8.8.8.8")
