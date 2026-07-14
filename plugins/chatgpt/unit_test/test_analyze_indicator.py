import unittest
from unittest.mock import MagicMock

from insightconnect_plugin_runtime.exceptions import PluginException

from komand_chatgpt.actions.analyze_indicator.action import AnalyzeIndicator
from komand_chatgpt.actions.analyze_indicator.schema import Input, Output
from unit_test.util import create_mock_action, load_fixture


class TestAnalyzeIndicator(unittest.TestCase):
    def setUp(self):
        self.action = create_mock_action(AnalyzeIndicator)
        self.mock_response = load_fixture("analyze_indicator_success.json")

    def test_analyze_ip_address(self):
        """Test analyzing an IP address indicator."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INDICATOR: "198.51.100.23",
                Input.INDICATOR_TYPE: "ip_address",
            }
        )

        self.assertIn(Output.ANALYSIS, result)
        self.assertIn(Output.RISK_ASSESSMENT, result)
        self.assertIn(Output.RECOMMENDED_ACTIONS, result)
        self.assertEqual(result[Output.RISK_ASSESSMENT], "HIGH - Associated with known C2 infrastructure")
        self.assertIsInstance(result[Output.RECOMMENDED_ACTIONS], list)
        self.assertGreater(len(result[Output.RECOMMENDED_ACTIONS]), 0)

    def test_analyze_with_context(self):
        """Test analyzing an indicator with additional context."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INDICATOR: "198.51.100.23",
                Input.INDICATOR_TYPE: "ip_address",
                Input.ADDITIONAL_CONTEXT: "Observed in outbound DNS traffic",
            }
        )

        self.assertIn(Output.ANALYSIS, result)
        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("Additional context", prompt_arg)

    def test_analyze_domain(self):
        """Test analyzing a domain indicator."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INDICATOR: "malicious-domain.xyz",
                Input.INDICATOR_TYPE: "domain",
            }
        )

        self.assertIn(Output.ANALYSIS, result)
        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("domain", prompt_arg)

    def test_analyze_file_hash(self):
        """Test analyzing a file hash indicator."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INDICATOR: "e99a18c428cb38d5f260853678922e03",
                Input.INDICATOR_TYPE: "file_hash",
            }
        )

        self.assertIn(Output.ANALYSIS, result)
        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("file hash", prompt_arg)

    def test_analyze_indicator_api_error(self):
        """Test that API errors propagate correctly."""
        self.action.connection.client.chat_completion_json.side_effect = PluginException(
            cause="Invalid API key provided",
            assistance="Verify that the OpenAI API key is correct",
        )

        with self.assertRaises(PluginException) as context:
            self.action.run(
                {
                    Input.INDICATOR: "198.51.100.23",
                    Input.INDICATOR_TYPE: "ip_address",
                }
            )

        self.assertIn("Invalid API key", context.exception.cause)
