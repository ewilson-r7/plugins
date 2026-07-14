import unittest
from unittest.mock import MagicMock

from insightconnect_plugin_runtime.exceptions import PluginException

from komand_chatgpt.actions.ask_chatgpt.action import AskChatgpt
from komand_chatgpt.actions.ask_chatgpt.schema import Input, Output
from unit_test.util import create_mock_action, load_fixture


class TestAskChatgpt(unittest.TestCase):
    def setUp(self):
        self.action = create_mock_action(AskChatgpt)
        self.mock_response = load_fixture("chat_completion_success.json")

    def test_ask_chatgpt_success(self):
        """Test successful prompt completion."""
        self.action.connection.client.chat_completion.return_value = self.mock_response

        result = self.action.run(
            {
                Input.PROMPT: "What are the common indicators of a phishing email?",
                Input.MAX_TOKENS: 2048,
                Input.TEMPERATURE: 0.7,
            }
        )

        self.assertIn(Output.RESPONSE, result)
        self.assertIn(Output.USAGE, result)
        self.assertEqual(result[Output.RESPONSE], self.mock_response["response"])
        self.assertEqual(result[Output.USAGE]["total_tokens"], 175)

        self.action.connection.client.chat_completion.assert_called_once_with(
            prompt="What are the common indicators of a phishing email?",
            system_message=None,
            max_tokens=2048,
            temperature=0.7,
        )

    def test_ask_chatgpt_with_system_message(self):
        """Test prompt completion with a system message."""
        self.action.connection.client.chat_completion.return_value = self.mock_response

        result = self.action.run(
            {
                Input.PROMPT: "Explain lateral movement",
                Input.SYSTEM_MESSAGE: "You are a cybersecurity analyst assistant",
                Input.MAX_TOKENS: 1024,
                Input.TEMPERATURE: 0.5,
            }
        )

        self.assertIn(Output.RESPONSE, result)
        self.action.connection.client.chat_completion.assert_called_once_with(
            prompt="Explain lateral movement",
            system_message="You are a cybersecurity analyst assistant",
            max_tokens=1024,
            temperature=0.5,
        )

    def test_ask_chatgpt_default_params(self):
        """Test prompt completion uses defaults when optional params not provided."""
        self.action.connection.client.chat_completion.return_value = self.mock_response

        result = self.action.run(
            {
                Input.PROMPT: "What is ransomware?",
            }
        )

        self.assertIn(Output.RESPONSE, result)
        self.action.connection.client.chat_completion.assert_called_once_with(
            prompt="What is ransomware?",
            system_message=None,
            max_tokens=2048,
            temperature=0.7,
        )

    def test_ask_chatgpt_api_error(self):
        """Test that API errors propagate as PluginException."""
        self.action.connection.client.chat_completion.side_effect = PluginException(
            cause="OpenAI API rate limit exceeded or quota exhausted",
            assistance="Reduce request frequency or check your usage limits",
        )

        with self.assertRaises(PluginException) as context:
            self.action.run(
                {
                    Input.PROMPT: "Test prompt",
                    Input.MAX_TOKENS: 2048,
                    Input.TEMPERATURE: 0.7,
                }
            )

        self.assertIn("rate limit", context.exception.cause)
