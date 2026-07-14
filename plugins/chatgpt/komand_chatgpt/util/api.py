import json
from typing import Union

import requests
from insightconnect_plugin_runtime.exceptions import PluginException

from .constants import (
    CHAT_COMPLETIONS_ENDPOINT,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    HTTP_ERROR_MAP,
    MODELS_ENDPOINT,
    OPENAI_BASE_URL,
    TIMEOUT,
)


class ChatGPTClient:
    def __init__(self, api_key: str, model: str, logger):
        self.api_key = api_key
        self.model = model
        self.logger = logger
        self.base_url = OPENAI_BASE_URL

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Union[dict, list]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._headers,
                timeout=TIMEOUT,
                **kwargs,
            )
        except requests.exceptions.Timeout as error:
            raise PluginException(
                cause="Request to OpenAI API timed out",
                assistance=f"The request exceeded the {TIMEOUT} second timeout. "
                "Try reducing the max_tokens value or simplifying the prompt",
                data=error,
            ) from error
        except requests.exceptions.ConnectionError as error:
            raise PluginException(
                cause="Unable to connect to the OpenAI API",
                assistance=f"Verify network connectivity to {self.base_url}. "
                "Check firewall rules and proxy settings",
                data=error,
            ) from error

        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Union[dict, list]:
        if response.status_code == 200:
            return self._parse_json(response)

        error_info = HTTP_ERROR_MAP.get(response.status_code)
        if error_info:
            raise PluginException(
                cause=error_info["cause"],
                assistance=error_info["assistance"],
                data=response.text,
            )

        raise PluginException(
            cause=f"Unexpected HTTP status code {response.status_code} from OpenAI API",
            assistance="Check the OpenAI API status page and try again",
            data=response.text,
        )

    @staticmethod
    def _parse_json(response: requests.Response) -> Union[dict, list]:
        try:
            return response.json()
        except json.JSONDecodeError as error:
            raise PluginException(
                cause="Received non-JSON response from OpenAI API",
                assistance="The API returned an unexpected response format. Try again later",
                data=error,
            ) from error

    def chat_completion(
        self,
        prompt: str,
        system_message: str = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        model: str = None,
    ) -> dict:
        """Send a chat completion request to the OpenAI API."""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        self.logger.info("Sending chat completion request to model: %s", payload["model"])
        response = self._make_request("POST", CHAT_COMPLETIONS_ENDPOINT, json=payload)

        return {
            "response": response["choices"][0]["message"]["content"].strip(),
            "usage": response.get("usage", {}),
        }

    def chat_completion_json(
        self,
        prompt: str,
        system_message: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = 0.3,
        model: str = None,
    ) -> dict:
        """Send a chat completion request expecting JSON output."""
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]

        payload = {
            "model": model or self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        self.logger.info("Sending structured JSON chat completion request to model: %s", payload["model"])
        response = self._make_request("POST", CHAT_COMPLETIONS_ENDPOINT, json=payload)

        content = response["choices"][0]["message"]["content"].strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError as error:
            self.logger.warning("Failed to parse structured response as JSON: %s", error)
            raise PluginException(
                cause="ChatGPT returned a response that could not be parsed as JSON",
                assistance="Try running the request again. If the issue persists, try a different model",
                data=content,
            ) from error

    def test_connection(self) -> bool:
        """Validate the API key by listing available models."""
        self.logger.info("Testing OpenAI API connection...")
        self._make_request("GET", MODELS_ENDPOINT)
        return True
