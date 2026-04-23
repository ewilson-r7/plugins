"""TeamDynamix API request helper."""
import requests
from insightconnect_plugin_runtime.exceptions import PluginException


class TeamDynamixClient:
    """Handles authentication and HTTP requests to the TeamDynamix Web API."""

    def __init__(self, base_url: str, beid: str, web_services_key: str, app_id: int, logger=None):
        self.base_url = base_url.rstrip("/")
        self.beid = beid
        self.web_services_key = web_services_key
        self.app_id = app_id
        self.logger = logger
        self._token = None
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def _authenticate(self) -> str:
        """Authenticate with TeamDynamix API using BEID and Web Services Key.
        Returns a bearer token string."""
        url = f"{self.base_url}/TDWebApi/api/auth/loginadmin"
        payload = {"BEID": self.beid, "WebServicesKey": self.web_services_key}

        if self.logger:
            self.logger.info(f"TeamDynamixClient: Authenticating at {url}")

        resp = self._session.post(url, json=payload, timeout=30)

        if resp.status_code != 200:
            raise PluginException(
                cause=f"TeamDynamix authentication failed with status {resp.status_code}.",
                assistance=f"Verify BEID and Web Services Key. Response: {resp.text}",
            )

        token = resp.text.strip().strip('"')
        if not token:
            raise PluginException(
                cause="TeamDynamix returned an empty authentication token.",
                assistance="Check BEID and Web Services Key in your connection settings.",
            )

        return token

    def _get_token(self) -> str:
        """Return a valid bearer token, authenticating if necessary."""
        if not self._token:
            self._token = self._authenticate()
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    def make_request(self, method: str, endpoint: str, payload: dict = None, params: dict = None) -> dict:
        """Make an authenticated request to the TeamDynamix API.

        Args:
            method: HTTP method ('get', 'post', 'patch', 'put', 'delete')
            endpoint: API endpoint path, e.g. '/TDWebApi/api/42/tickets'
            payload: JSON body dict (for POST/PATCH/PUT)
            params: Query parameters dict

        Returns:
            Parsed JSON response dict, or empty dict for 204 responses.

        Raises:
            PluginException on HTTP errors.
        """
        url = f"{self.base_url}{endpoint}"
        if self.logger:
            self.logger.info(f"TeamDynamixClient: {method.upper()} {url}")

        resp = self._session.request(
            method=method.upper(),
            url=url,
            headers=self._headers(),
            json=payload,
            params=params,
            timeout=30,
        )

        # Handle token expiry with one retry
        if resp.status_code == 401:
            if self.logger:
                self.logger.info("TeamDynamixClient: Token expired, re-authenticating...")
            self._token = self._authenticate()
            resp = self._session.request(
                method=method.upper(),
                url=url,
                headers=self._headers(),
                json=payload,
                params=params,
                timeout=30,
            )

        if resp.status_code == 204:
            return {}

        if resp.status_code not in range(200, 300):
            raise PluginException(
                cause=f"TeamDynamix API returned status {resp.status_code}.",
                assistance=f"Response: {resp.text}",
            )

        try:
            return resp.json()
        except ValueError:
            raise PluginException(
                cause="TeamDynamix API returned non-JSON response.",
                assistance=f"Raw response: {resp.text}",
            )

    def test(self) -> bool:
        """Test the connection by fetching minimal ticket data."""
        self.make_request("post", f"/TDWebApi/api/{self.app_id}/tickets/search", payload={"MaxResults": 1})
        return True
