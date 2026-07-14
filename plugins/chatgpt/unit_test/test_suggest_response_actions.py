import unittest
from unittest.mock import MagicMock

from insightconnect_plugin_runtime.exceptions import PluginException

from komand_chatgpt.actions.suggest_response_actions.action import SuggestResponseActions
from komand_chatgpt.actions.suggest_response_actions.schema import Input, Output
from unit_test.util import create_mock_action, load_fixture


class TestSuggestResponseActions(unittest.TestCase):
    def setUp(self):
        self.action = create_mock_action(SuggestResponseActions)
        self.mock_response = load_fixture("suggest_response_success.json")

    def test_suggest_response_containment(self):
        """Test getting response suggestions during containment phase."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INCIDENT_DESCRIPTION: "Ransomware detected encrypting files on three workstations.",
                Input.RESPONSE_PHASE: "containment",
            }
        )

        self.assertIn(Output.IMMEDIATE_ACTIONS, result)
        self.assertIn(Output.INVESTIGATION_STEPS, result)
        self.assertIn(Output.LONG_TERM_RECOMMENDATIONS, result)
        self.assertIsInstance(result[Output.IMMEDIATE_ACTIONS], list)
        self.assertGreater(len(result[Output.IMMEDIATE_ACTIONS]), 0)

    def test_suggest_response_with_environment_context(self):
        """Test that environment context is included in the prompt."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INCIDENT_DESCRIPTION: "Data exfiltration detected",
                Input.ENVIRONMENT_CONTEXT: "500 endpoint Windows domain",
                Input.RESPONSE_PHASE: "identification",
            }
        )

        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("500 endpoint Windows domain", prompt_arg)

    def test_suggest_response_eradication_phase(self):
        """Test recommendations for eradication phase."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INCIDENT_DESCRIPTION: "Backdoor found on web server",
                Input.RESPONSE_PHASE: "eradication",
            }
        )

        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("eradication", prompt_arg)

    def test_suggest_response_defaults(self):
        """Test defaults when optional params not provided."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INCIDENT_DESCRIPTION: "Suspicious login from foreign IP",
            }
        )

        self.assertIn(Output.IMMEDIATE_ACTIONS, result)
        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("containment", prompt_arg)

    def test_suggest_response_api_error(self):
        """Test that API errors propagate correctly."""
        self.action.connection.client.chat_completion_json.side_effect = PluginException(
            cause="OpenAI service temporarily unavailable",
            assistance="Try again in a few moments",
        )

        with self.assertRaises(PluginException):
            self.action.run(
                {
                    Input.INCIDENT_DESCRIPTION: "Test incident",
                }
            )
