import requests
from logging import Logger
from insightconnect_plugin_runtime.exceptions import PluginException
from icon_halo_itsm.util.constants import (
    TIMEOUT,
    AUTH_ENDPOINT,
    TICKETS_ENDPOINT,
    HTTP_ERROR_MAP,
)


class HaloItsmApi:
    def __init__(self, base_url: str, client_id: str, client_secret: str, tenant: str, logger: Logger):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant = tenant
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
        self._access_token = None

    def _authenticate(self) -> None:
        """Obtain an OAuth 2.0 access token using client credentials."""
        auth_url = f"{self.base_url}{AUTH_ENDPOINT}"
        if self.tenant:
            auth_url = f"{auth_url}?tenant={self.tenant}"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "all",
        }

        try:
            response = requests.post(
                auth_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise PluginException(preset=PluginException.Preset.TIMEOUT)
        except requests.exceptions.ConnectionError as error:
            raise PluginException(
                cause="Connection error occurred during authentication.",
                assistance="Check that the Base URL is correct and reachable.",
                data=str(error),
            )

        if response.status_code != 200:
            raise PluginException(
                cause="Authentication failed.",
                assistance="Verify that the Client ID, Client Secret, and Tenant are correct. "
                "Ensure the API application is configured with the Client Credentials grant type.",
                data=response.text,
            )

        try:
            token_data = response.json()
        except ValueError:
            raise PluginException(preset=PluginException.Preset.INVALID_JSON, data=response.text)

        self._access_token = token_data.get("access_token")
        if not self._access_token:
            raise PluginException(
                cause="No access token returned from authentication endpoint.",
                assistance="Verify the API application configuration in Halo ITSM.",
                data=response.text,
            )
        self.session.headers.update({"Authorization": f"Bearer {self._access_token}"})

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token before making requests."""
        if not self._access_token:
            self._authenticate()

    def _make_request(self, method: str, endpoint: str, params: dict = None, json_data=None) -> dict:
        """Make an authenticated request to the Halo ITSM API."""
        self._ensure_authenticated()
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, timeout=TIMEOUT, params=params, json=json_data)
        except requests.exceptions.Timeout:
            raise PluginException(preset=PluginException.Preset.TIMEOUT)
        except requests.exceptions.ConnectionError as error:
            raise PluginException(
                cause="Connection error occurred.",
                assistance="Check that the Base URL is reachable.",
                data=str(error),
            )

        # If we get a 401, try re-authenticating once
        if response.status_code == 401:
            self._access_token = None
            self._authenticate()
            try:
                response = self.session.request(method, url, timeout=TIMEOUT, params=params, json=json_data)
            except requests.exceptions.Timeout:
                raise PluginException(preset=PluginException.Preset.TIMEOUT)
            except requests.exceptions.ConnectionError as error:
                raise PluginException(
                    cause="Connection error occurred.",
                    assistance="Check that the Base URL is reachable.",
                    data=str(error),
                )

        self._handle_status(response)

        if response.status_code == 204 or not response.text:
            return {}

        try:
            return response.json()
        except ValueError:
            raise PluginException(preset=PluginException.Preset.INVALID_JSON, data=response.text)

    def _handle_status(self, response: requests.Response) -> None:
        """Handle non-success HTTP status codes."""
        if response.status_code in (200, 201, 204):
            return

        error = HTTP_ERROR_MAP.get(response.status_code)
        if error:
            raise PluginException(cause=error["cause"], assistance=error["assistance"], data=response.text)

        raise PluginException(
            cause=f"Unexpected status code: {response.status_code}.",
            assistance="Check the Halo ITSM API documentation for this status code.",
            data=response.text,
        )

    def test_connection(self) -> None:
        """Test the connection by authenticating and retrieving a single ticket."""
        self._authenticate()
        self._make_request("GET", TICKETS_ENDPOINT, params={"count": 1})

    def create_ticket(self, ticket_data: dict) -> dict:
        """Create a new ticket."""
        # Halo ITSM expects a list of tickets in POST body
        response = self._make_request("POST", TICKETS_ENDPOINT, json_data=[ticket_data])
        # Response is typically the created ticket object or a list
        if isinstance(response, list) and len(response) > 0:
            return response[0]
        return response

    def get_ticket(self, ticket_id: int) -> dict:
        """Get a ticket by ID."""
        return self._make_request("GET", f"{TICKETS_ENDPOINT}/{ticket_id}")

    def update_ticket(self, ticket_id: int, ticket_data: dict) -> dict:
        """Update an existing ticket."""
        ticket_data["id"] = ticket_id
        response = self._make_request("POST", TICKETS_ENDPOINT, json_data=[ticket_data])
        if isinstance(response, list) and len(response) > 0:
            return response[0]
        return response

    def delete_ticket(self, ticket_id: int) -> None:
        """Delete a ticket by ID."""
        self._make_request("DELETE", f"{TICKETS_ENDPOINT}/{ticket_id}")

    def list_tickets(self, params: dict = None) -> list:
        """List tickets with optional filtering."""
        response = self._make_request("GET", TICKETS_ENDPOINT, params=params)
        if isinstance(response, dict):
            return response.get("tickets", response.get("records", []))
        if isinstance(response, list):
            return response
        return []

    def add_action_to_ticket(self, ticket_id: int, action_data: dict) -> dict:
        """Add an action (note/comment) to a ticket."""
        endpoint = f"{TICKETS_ENDPOINT}/{ticket_id}/actions"
        response = self._make_request("POST", endpoint, json_data=[action_data])
        if isinstance(response, list) and len(response) > 0:
            return response[0]
        return response

    def attach_file_to_ticket(self, ticket_id: int, filename: str, content: str, note: str, hiddenfromuser: bool = False) -> dict:
        """Attach a file to a ticket via an action with multipart form data."""
        import base64

        self._ensure_authenticated()
        endpoint = f"{TICKETS_ENDPOINT}/{ticket_id}/actions"
        url = f"{self.base_url}{endpoint}"

        # Decode base64 content
        try:
            file_bytes = base64.b64decode(content)
        except Exception as error:
            raise PluginException(
                cause="Failed to decode file content.",
                assistance="Ensure the content is valid Base64-encoded data.",
                data=str(error),
            )

        # Build multipart form data — Halo expects the action metadata plus the file
        files = {
            "file": (filename, file_bytes),
        }
        data = {
            "note": note,
            "hiddenfromuser": str(hiddenfromuser).lower(),
            "ticket_id": str(ticket_id),
        }

        # Remove the Content-Type header for multipart (requests will set it with boundary)
        headers = {k: v for k, v in self.session.headers.items() if k.lower() != "content-type"}

        try:
            response = self.session.post(url, timeout=TIMEOUT, files=files, data=data, headers=headers)
        except requests.exceptions.Timeout:
            raise PluginException(preset=PluginException.Preset.TIMEOUT)
        except requests.exceptions.ConnectionError as error:
            raise PluginException(
                cause="Connection error occurred.",
                assistance="Check that the Base URL is reachable.",
                data=str(error),
            )

        # Handle 401 with re-auth
        if response.status_code == 401:
            self._access_token = None
            self._authenticate()
            headers["Authorization"] = f"Bearer {self._access_token}"
            try:
                response = self.session.post(url, timeout=TIMEOUT, files=files, data=data, headers=headers)
            except requests.exceptions.Timeout:
                raise PluginException(preset=PluginException.Preset.TIMEOUT)
            except requests.exceptions.ConnectionError as error:
                raise PluginException(
                    cause="Connection error occurred.",
                    assistance="Check that the Base URL is reachable.",
                    data=str(error),
                )

        self._handle_status(response)

        if response.status_code == 204 or not response.text:
            return {}

        try:
            result = response.json()
        except ValueError:
            raise PluginException(preset=PluginException.Preset.INVALID_JSON, data=response.text)

        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result
