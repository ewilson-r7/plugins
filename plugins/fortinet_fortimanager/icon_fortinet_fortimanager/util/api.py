import json
from logging import Logger
from typing import Optional

import requests
from insightconnect_plugin_runtime.exceptions import PluginException

from icon_fortinet_fortimanager.util.constants import (
    ERROR_CODE_INVALID_PARAMS,
    ERROR_CODE_NO_PERMISSION,
    ERROR_CODE_OBJECT_ALREADY_EXISTS,
    ERROR_CODE_OBJECT_NOT_EXIST,
    ERROR_CODE_SESSION_EXPIRED,
    ERROR_CODE_SUCCESS,
    ERROR_MESSAGES,
    METHOD_ADD,
    METHOD_DELETE,
    METHOD_EXEC,
    METHOD_GET,
    METHOD_UPDATE,
    URL_ADDRESS_GROUP,
    URL_ADDRESS_GROUPS,
    URL_ADDRESS_OBJECTS,
    URL_INSTALL_PACKAGE,
    URL_LOGIN,
    URL_LOGOUT,
    URL_POLICIES,
    URL_SYSTEM_STATUS,
)
from icon_fortinet_fortimanager.util.helpers import Helpers


class SessionExpiredError(Exception):
    """Internal exception raised when JSON-RPC returns error code -10 (session expired)."""

    pass


class FortiManagerAPI:
    """
    JSON-RPC client for FortiManager.
    Supports dual authentication: API Token (Bearer, recommended) and Session-Based (legacy).
    """

    REQUEST_TIMEOUT = 30

    def __init__(
        self,
        host: str,
        logger: Logger,
        ssl_verify: bool = False,
        auth_type: str = "API Token",
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.base_url = f"https://{host}/jsonrpc"
        self.logger = logger
        self.ssl_verify = ssl_verify
        self.auth_type = auth_type
        self.api_key = api_key
        self.username = username
        self.password = password
        self.session_token: Optional[str] = None
        self.request_id: int = 1

        # Set up requests session
        self._session = requests.Session()
        self._session.verify = self.ssl_verify

    def login(self) -> str:
        """Authenticate using session-based auth and store the session token.

        Returns:
            The session token string.

        Raises:
            PluginException: If login fails.
        """
        payload = {
            "id": self._next_id(),
            "method": METHOD_EXEC,
            "params": [
                {
                    "url": URL_LOGIN,
                    "data": {
                        "user": self.username,
                        "passwd": self.password,
                    },
                }
            ],
        }

        self._log_request(METHOD_EXEC, URL_LOGIN, payload)

        try:
            response = self._session.post(
                self.base_url,
                json=payload,
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.exceptions.SSLError as error:
            raise PluginException(
                cause="SSL certificate validation failed.",
                assistance="Verify the FortiManager TLS certificate or disable SSL verification.",
                data=str(error),
            ) from error
        except requests.exceptions.ConnectionError as error:
            raise PluginException(
                cause="Unable to connect to FortiManager.",
                assistance="Verify the hostname and network connectivity.",
                data=str(error),
            ) from error
        except requests.exceptions.Timeout as error:
            raise PluginException(
                cause="Connection to FortiManager timed out.",
                assistance="Verify the hostname and network connectivity.",
                data=str(error),
            ) from error
        except (requests.exceptions.RequestException, json.JSONDecodeError) as error:
            raise PluginException(
                cause="Failed to communicate with FortiManager.",
                assistance="Verify the hostname and network connectivity.",
                data=str(error),
            ) from error

        self._log_response(response_data)

        # Extract session token from response
        session = response_data.get("session")
        if not session:
            # Check for error in result
            result = response_data.get("result", [{}])[0]
            status = result.get("status", {})
            code = status.get("code", -1)
            if code != ERROR_CODE_SUCCESS:
                message = status.get("message", "Login failed")
                raise PluginException(
                    cause=f"FortiManager login failed (code {code}): {message}",
                    assistance="Verify your username and password credentials.",
                    data=str(response_data),
                )
            raise PluginException(
                cause="FortiManager login failed: no session token returned.",
                assistance="Verify your username and password credentials.",
                data=str(response_data),
            )

        self.session_token = session
        self.logger.info("Successfully authenticated with FortiManager (session-based).")
        return self.session_token

    def logout(self) -> None:
        """Logout from session-based authentication and clear the session token.

        Raises:
            PluginException: If logout fails.
        """
        if not self.session_token:
            return

        payload = {
            "id": self._next_id(),
            "method": METHOD_EXEC,
            "params": [{"url": URL_LOGOUT}],
            "session": self.session_token,
        }

        self._log_request(METHOD_EXEC, URL_LOGOUT, payload)

        try:
            response = self._session.post(
                self.base_url,
                json=payload,
                timeout=self.REQUEST_TIMEOUT,
            )
            response_data = response.json()
            self._log_response(response_data)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as error:
            self.logger.warning("Logout request failed: %s", error)
        finally:
            self.session_token = None

    def execute(self, method: str, url: str, data: Optional[dict] = None, params: Optional[list] = None) -> dict:
        """Execute a JSON-RPC request against FortiManager.

        Routes to the appropriate authentication strategy (Bearer or session-based).
        For session-based auth, handles error -10 with one retry after re-authentication.

        Args:
            method: JSON-RPC method (get, add, set, update, delete, exec).
            url: The JSON-RPC URL path.
            data: Optional data payload for the request.
            params: Optional pre-built params list (overrides url/data construction).

        Returns:
            Parsed response data from FortiManager.

        Raises:
            PluginException: On API errors.
        """
        if self.auth_type == "API Token":
            return self._execute_with_bearer(method, url, data, params)

        # Session-based auth with retry on session expiry
        try:
            return self._execute_with_session(method, url, data, params)
        except SessionExpiredError:
            self.logger.info("Session expired, re-authenticating...")
            self.login()
            return self._execute_with_session(method, url, data, params)

    def get_address_objects(self, adom: str) -> list:
        """Retrieve all address objects from the specified ADOM.

        Args:
            adom: The ADOM name.

        Returns:
            List of address object dictionaries.
        """
        url = URL_ADDRESS_OBJECTS.format(adom=adom)
        result = self.execute(METHOD_GET, url)
        if isinstance(result, list):
            return result
        return result.get("data", []) if isinstance(result, dict) else []

    def create_address_object(self, adom: str, name: str, address_type: str, value: str) -> dict:
        """Create a new address object in the specified ADOM.

        Args:
            adom: The ADOM name.
            name: The address object name.
            address_type: The type ('ipmask' or 'fqdn').
            value: The address value (CIDR or FQDN).

        Returns:
            The created address object data.
        """
        url = URL_ADDRESS_OBJECTS.format(adom=adom)
        data = {"name": name, "type": address_type}

        if address_type == "ipmask":
            data["subnet"] = value
        elif address_type == "fqdn":
            data["fqdn"] = value

        return self.execute(METHOD_ADD, url, data=data)

    def delete_address_object(self, adom: str, name: str) -> dict:
        """Delete an address object from the specified ADOM.

        Args:
            adom: The ADOM name.
            name: The address object name to delete.

        Returns:
            Response data from the API.
        """
        url = URL_ADDRESS_OBJECTS.format(adom=adom) + f"/{name}"
        return self.execute(METHOD_DELETE, url)

    def get_address_group(self, adom: str, group_name: str) -> dict:
        """Retrieve an address group from the specified ADOM.

        Args:
            adom: The ADOM name.
            group_name: The address group name.

        Returns:
            The address group dictionary.
        """
        url = URL_ADDRESS_GROUP.format(adom=adom, name=group_name)
        return self.execute(METHOD_GET, url)

    def update_address_group(self, adom: str, group_name: str, members: list) -> dict:
        """Update an address group's member list.

        Args:
            adom: The ADOM name.
            group_name: The address group name.
            members: The updated list of member address object names.

        Returns:
            Response data from the API.
        """
        url = URL_ADDRESS_GROUP.format(adom=adom, name=group_name)
        data = {"member": members}
        return self.execute(METHOD_UPDATE, url, data=data)

    def get_policies(self, adom: str, package: str) -> list:
        """Retrieve firewall policies from a policy package.

        Args:
            adom: The ADOM name.
            package: The policy package name.

        Returns:
            List of policy dictionaries.
        """
        url = URL_POLICIES.format(adom=adom, package=package)
        result = self.execute(METHOD_GET, url)
        if isinstance(result, list):
            return result
        return result.get("data", []) if isinstance(result, dict) else []

    def install_policy_package(self, adom: str, package: str, targets: list) -> int:
        """Install a policy package to target devices/device groups.

        Args:
            adom: The ADOM name.
            package: The policy package name.
            targets: List of target scope dicts (e.g. [{"name": "device1", "vdom": "root"}]).

        Returns:
            The task ID for the initiated install operation.
        """
        url = URL_INSTALL_PACKAGE
        data = {
            "adom": adom,
            "pkg": package,
            "scope": targets,
        }
        result = self.execute(METHOD_EXEC, url, data=data)
        # Extract task ID from response
        if isinstance(result, dict):
            return result.get("task", 0)
        return 0

    # --- Private methods ---

    def _execute_with_bearer(
        self, method: str, url: str, data: Optional[dict] = None, params: Optional[list] = None
    ) -> dict:
        """Execute a request using API Token (Bearer) authentication."""
        payload = self._build_payload(method, url, data, params)

        self._log_request(method, url, payload)

        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = self._session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.exceptions.SSLError as error:
            raise PluginException(
                cause="SSL certificate validation failed.",
                assistance="Verify the FortiManager TLS certificate or disable SSL verification.",
                data=str(error),
            ) from error
        except requests.exceptions.ConnectionError as error:
            raise PluginException(
                cause="Unable to connect to FortiManager.",
                assistance="Verify the hostname and network connectivity.",
                data=str(error),
            ) from error
        except requests.exceptions.Timeout as error:
            raise PluginException(
                cause="Connection to FortiManager timed out.",
                assistance="Verify the hostname and network connectivity.",
                data=str(error),
            ) from error
        except requests.exceptions.HTTPError as error:
            raise PluginException(
                cause=f"HTTP error from FortiManager: {error.response.status_code}",
                assistance="Verify the API key and FortiManager configuration.",
                data=str(error),
            ) from error
        except (requests.exceptions.RequestException, json.JSONDecodeError) as error:
            raise PluginException(
                cause="Failed to communicate with FortiManager.",
                assistance="Verify the hostname and network connectivity.",
                data=str(error),
            ) from error

        self._log_response(response_data)
        return self._handle_response(response_data, method, url)

    def _execute_with_session(
        self, method: str, url: str, data: Optional[dict] = None, params: Optional[list] = None
    ) -> dict:
        """Execute a request using session-based authentication."""
        if not self.session_token:
            self.login()

        payload = self._build_payload(method, url, data, params)
        payload["session"] = self.session_token

        self._log_request(method, url, payload)

        try:
            response = self._session.post(
                self.base_url,
                json=payload,
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.exceptions.SSLError as error:
            raise PluginException(
                cause="SSL certificate validation failed.",
                assistance="Verify the FortiManager TLS certificate or disable SSL verification.",
                data=str(error),
            ) from error
        except requests.exceptions.ConnectionError as error:
            raise PluginException(
                cause="Unable to connect to FortiManager.",
                assistance="Verify the hostname and network connectivity.",
                data=str(error),
            ) from error
        except requests.exceptions.Timeout as error:
            raise PluginException(
                cause="Connection to FortiManager timed out.",
                assistance="Verify the hostname and network connectivity.",
                data=str(error),
            ) from error
        except requests.exceptions.HTTPError as error:
            raise PluginException(
                cause=f"HTTP error from FortiManager: {error.response.status_code}",
                assistance="Verify the credentials and FortiManager configuration.",
                data=str(error),
            ) from error
        except (requests.exceptions.RequestException, json.JSONDecodeError) as error:
            raise PluginException(
                cause="Failed to communicate with FortiManager.",
                assistance="Verify the hostname and network connectivity.",
                data=str(error),
            ) from error

        self._log_response(response_data)
        return self._handle_response(response_data, method, url)

    def _build_payload(self, method: str, url: str, data: Optional[dict] = None, params: Optional[list] = None) -> dict:
        """Build the JSON-RPC request envelope.

        Args:
            method: JSON-RPC method.
            url: The URL path for the operation.
            data: Optional data payload.
            params: Optional pre-built params list.

        Returns:
            The JSON-RPC payload dictionary.
        """
        if params is not None:
            return {
                "id": self._next_id(),
                "method": method,
                "params": params,
            }

        param_entry = {"url": url}
        if data is not None:
            param_entry["data"] = data

        return {
            "id": self._next_id(),
            "method": method,
            "params": [param_entry],
        }

    def _handle_response(self, response: dict, method: str, url: str) -> dict:
        """Parse the JSON-RPC response and handle error codes.

        Args:
            response: The raw JSON-RPC response dictionary.
            method: The method that was called (for error context).
            url: The URL that was called (for error context).

        Returns:
            The result data from a successful response.

        Raises:
            SessionExpiredError: If error code -10 is returned.
            PluginException: For all other error codes.
        """
        result = response.get("result", [{}])
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
        elif isinstance(result, list):
            result = {}

        status = result.get("status", {})
        code = status.get("code", 0)

        if code == ERROR_CODE_SUCCESS:
            return result.get("data", result)

        if code == ERROR_CODE_SESSION_EXPIRED:
            raise SessionExpiredError()

        # Map known error codes to descriptive messages
        error_message = ERROR_MESSAGES.get(code, status.get("message", "Unknown error"))

        raise PluginException(
            cause=f"FortiManager API error (code {code}): {error_message}",
            assistance="Verify the input parameters and ADOM configuration.",
            data=str(result),
        )

    def _next_id(self) -> int:
        """Generate the next request ID and increment the counter."""
        current_id = self.request_id
        self.request_id += 1
        return current_id

    def _log_request(self, method: str, url: str, payload: dict) -> None:
        """Log request details with sensitive values redacted."""
        # Build list of sensitive values to redact
        sensitive_values = [v for v in [self.api_key, self.password, self.session_token] if v]

        log_message = f"FortiManager API request: method={method}, url={url}"
        redacted_message = Helpers.redact_sensitive(log_message, sensitive_values)
        self.logger.debug(redacted_message)

        # Log redacted params
        try:
            params_str = json.dumps(payload.get("params", []))
            redacted_params = Helpers.redact_sensitive(params_str, sensitive_values)
            self.logger.debug("Request params: %s", redacted_params)
        except (TypeError, ValueError):
            self.logger.debug("Request params: [unable to serialize]")

    def _log_response(self, response_data: dict) -> None:
        """Log response status with sensitive values redacted."""
        sensitive_values = [v for v in [self.api_key, self.password, self.session_token] if v]

        # Extract status code from response
        result = response_data.get("result", [{}])
        if isinstance(result, list) and len(result) > 0:
            status = result[0].get("status", {})
            code = status.get("code", "N/A")
            message = status.get("message", "")
        else:
            code = "N/A"
            message = ""

        log_message = f"FortiManager API response: code={code}, message={message}"
        redacted_message = Helpers.redact_sensitive(log_message, sensitive_values)
        self.logger.debug(redacted_message)
