import unittest
from unittest.mock import MagicMock

from insightconnect_plugin_runtime.exceptions import PluginException

from komand_chatgpt.actions.summarize_incident.action import SummarizeIncident
from komand_chatgpt.actions.summarize_incident.schema import Input, Output
from unit_test.util import create_mock_action, load_fixture


class TestSummarizeIncident(unittest.TestCase):
    def setUp(self):
        self.action = create_mock_action(SummarizeIncident)
        self.mock_response = load_fixture("summarize_incident_success.json")

    def test_summarize_incident_technical(self):
        """Test summarizing an incident for a technical audience."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INCIDENT_DATA: "Alert: Malware detected on WORKSTATION-045. C2 callbacks observed.",
                Input.SEVERITY: "high",
                Input.AUDIENCE: "technical",
            }
        )

        self.assertIn(Output.SUMMARY, result)
        self.assertIn(Output.TIMELINE, result)
        self.assertIn(Output.KEY_FINDINGS, result)
        self.assertIsInstance(result[Output.KEY_FINDINGS], list)
        self.assertGreater(len(result[Output.KEY_FINDINGS]), 0)

    def test_summarize_incident_executive(self):
        """Test summarizing for an executive audience."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INCIDENT_DATA: "Multiple failed login attempts from external IPs",
                Input.AUDIENCE: "executive",
            }
        )

        self.assertIn(Output.SUMMARY, result)
        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("executive", prompt_arg)

    def test_summarize_incident_with_severity(self):
        """Test that severity is included in the prompt."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INCIDENT_DATA: "Ransomware detected on endpoints",
                Input.SEVERITY: "critical",
                Input.AUDIENCE: "both",
            }
        )

        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("CRITICAL", prompt_arg)

    def test_summarize_incident_defaults(self):
        """Test that defaults are applied when optional params missing."""
        self.action.connection.client.chat_completion_json.return_value = self.mock_response

        result = self.action.run(
            {
                Input.INCIDENT_DATA: "Suspicious network activity observed",
            }
        )

        self.assertIn(Output.SUMMARY, result)
        call_args = self.action.connection.client.chat_completion_json.call_args
        prompt_arg = call_args[1]["prompt"] if "prompt" in (call_args[1] or {}) else call_args[0][0]
        self.assertIn("technical", prompt_arg)

    def test_summarize_incident_api_error(self):
        """Test that API errors propagate correctly."""
        self.action.connection.client.chat_completion_json.side_effect = PluginException(
            cause="Request to OpenAI API timed out",
            assistance="Try reducing the max_tokens value",
        )

        with self.assertRaises(PluginException):
            self.action.run(
                {
                    Input.INCIDENT_DATA: "Test incident",
                    Input.AUDIENCE: "technical",
                }
            )
