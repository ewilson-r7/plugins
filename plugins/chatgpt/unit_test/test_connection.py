import json
import unittest
from unittest.mock import MagicMock, patch

from insightconnect_plugin_runtime.exceptions import PluginException

from komand_chatgpt.util.api import ChatGPTClient
from komand_chatgpt.util.constants import OPENAI_BASE_URL, TIMEOUT

import requests


class MockResponse:
    """Mock requests.Response object."""

    def __init__(self, status_code: int, json_data: dict = None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text or (json.dumps(json_data) if json_data else "")

    def json(self):
        if self._json_data is None:
            raise json.JSONDecodeError("No JSON", "", 0)
        return self._json_data


class TestChatGPTClient(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.client = ChatGPTClient(
            api_key="sk-test-key-123",
            model="gpt-4o",
            logger=self.logger,
        )

    @patch("komand_chatgpt.util.api.requests.request")
    def test_connection_success(self, mock_request):
        """Test successful connection test."""
        mock_request.return_value = MockResponse(200, {"data": [{"id": "gpt-4o"}]})

        result = self.client.test_connection()
        self.assertTrue(result)
        mock_request.assert_called_once_with(
            method="GET",
            url=f"{OPENAI_BASE_URL}/v1/models",
            headers=self.client._headers,
            timeout=TIMEOUT,
        )

    @patch("komand_chatgpt.util.api.requests.request")
    def test_connection_unauthorized(self, mock_request):
        """Test connection with invalid API key."""
        mock_request.return_value = MockResponse(401, text="Unauthorized")

        with self.assertRaises(PluginException) as context:
            self.client.test_connection()

        self.assertIn("Invalid API key", context.exception.cause)

    @patch("komand_chatgpt.util.api.requests.request")
    def test_chat_completion_success(self, mock_request):
        """Test successful chat completion."""
        mock_request.return_value = MockResponse(
            200,
            {
                "choices": [{"message": {"content": "Test response"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )

        result = self.client.chat_completion(prompt="Hello", max_tokens=100)

        self.assertEqual(result["response"], "Test response")
        self.assertEqual(result["usage"]["total_tokens"], 15)

    @patch("komand_chatgpt.util.api.requests.request")
    def test_chat_completion_with_system_message(self, mock_request):
        """Test chat completion includes system message in payload."""
        mock_request.return_value = MockResponse(
            200,
            {
                "choices": [{"message": {"content": "Response"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )

        self.client.chat_completion(
            prompt="Analyze this",
            system_message="You are a SOC analyst",
        )

        call_kwargs = mock_request.call_args[1]
        payload = call_kwargs["json"]
        self.assertEqual(len(payload["messages"]), 2)
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][0]["content"], "You are a SOC analyst")

    @patch("komand_chatgpt.util.api.requests.request")
    def test_chat_completion_json_success(self, mock_request):
        """Test structured JSON chat completion."""
        json_response = {"analysis": "Test analysis", "risk": "HIGH"}
        mock_request.return_value = MockResponse(
            200,
            {
                "choices": [{"message": {"content": json.dumps(json_response)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            },
        )

        result = self.client.chat_completion_json(
            prompt="Analyze IOC",
            system_message="You are an analyst",
        )

        self.assertEqual(result["analysis"], "Test analysis")
        self.assertEqual(result["risk"], "HIGH")

    @patch("komand_chatgpt.util.api.requests.request")
    def test_chat_completion_json_parse_failure(self, mock_request):
        """Test handling of non-JSON response from structured endpoint."""
        mock_request.return_value = MockResponse(
            200,
            {
                "choices": [{"message": {"content": "This is not valid JSON"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )

        with self.assertRaises(PluginException) as context:
            self.client.chat_completion_json(
                prompt="Analyze",
                system_message="Return JSON",
            )

        self.assertIn("could not be parsed as JSON", context.exception.cause)

    @patch("komand_chatgpt.util.api.requests.request")
    def test_timeout_error(self, mock_request):
        """Test timeout handling."""
        mock_request.side_effect = requests.exceptions.Timeout("Connection timed out")

        with self.assertRaises(PluginException) as context:
            self.client.chat_completion(prompt="Test")

        self.assertIn("timed out", context.exception.cause)

    @patch("komand_chatgpt.util.api.requests.request")
    def test_connection_error(self, mock_request):
        """Test connection error handling."""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection refused")

        with self.assertRaises(PluginException) as context:
            self.client.chat_completion(prompt="Test")

        self.assertIn("Unable to connect", context.exception.cause)

    @patch("komand_chatgpt.util.api.requests.request")
    def test_rate_limit_error(self, mock_request):
        """Test 429 rate limit error handling."""
        mock_request.return_value = MockResponse(429, text="Rate limit exceeded")

        with self.assertRaises(PluginException) as context:
            self.client.chat_completion(prompt="Test")

        self.assertIn("rate limit", context.exception.cause)

    @patch("komand_chatgpt.util.api.requests.request")
    def test_server_error(self, mock_request):
        """Test 500 server error handling."""
        mock_request.return_value = MockResponse(500, text="Internal Server Error")

        with self.assertRaises(PluginException) as context:
            self.client.chat_completion(prompt="Test")

        self.assertIn("Internal server error", context.exception.cause)

    @patch("komand_chatgpt.util.api.requests.request")
    def test_bad_request_error(self, mock_request):
        """Test 400 bad request error handling."""
        mock_request.return_value = MockResponse(400, text="Bad Request")

        with self.assertRaises(PluginException) as context:
            self.client.chat_completion(prompt="Test")

        self.assertIn("Bad request", context.exception.cause)

    @patch("komand_chatgpt.util.api.requests.request")
    def test_non_json_response(self, mock_request):
        """Test handling of non-JSON 200 response."""
        response = MockResponse(200)
        response._json_data = None
        mock_request.return_value = response

        with self.assertRaises(PluginException) as context:
            self.client.chat_completion(prompt="Test")

        self.assertIn("non-JSON", context.exception.cause)

    @patch("komand_chatgpt.util.api.requests.request")
    def test_unknown_status_code(self, mock_request):
        """Test handling of unmapped HTTP status code."""
        mock_request.return_value = MockResponse(418, text="I'm a teapot")

        with self.assertRaises(PluginException) as context:
            self.client.chat_completion(prompt="Test")

        self.assertIn("Unexpected HTTP status code 418", context.exception.cause)
