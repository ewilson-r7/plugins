import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import SummarizeIncidentInput, SummarizeIncidentOutput, Input, Output, Component
from ...util.constants import SUMMARIZE_INCIDENT_SYSTEM_PROMPT


class SummarizeIncident(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="summarize_incident",
            description=Component.DESCRIPTION,
            input=SummarizeIncidentInput(),
            output=SummarizeIncidentOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        audience = params.get(Input.AUDIENCE)
        incident_data = params.get(Input.INCIDENT_DATA)
        severity = params.get(Input.SEVERITY)
        # END INPUT BINDING - DO NOT REMOVE

        audience = audience or "technical"

        prompt_parts = [
            f"Summarize the following security incident for a {audience} audience.",
        ]

        if severity:
            prompt_parts.append(f"Incident severity: {severity.upper()}")

        prompt_parts.append(f"Incident data:\n{incident_data}")
        prompt_parts.append(
            "Provide a concise summary, timeline of events, and key findings."
        )

        prompt = "\n\n".join(prompt_parts)

        self.logger.info(
            "Summarizing incident for %s audience (severity: %s)", audience, severity or "not specified"
        )

        result = self.connection.client.chat_completion_json(
            prompt=prompt,
            system_message=SUMMARIZE_INCIDENT_SYSTEM_PROMPT,
            temperature=0.3,
        )

        return clean(
            {
                Output.SUMMARY: result.get("summary", ""),
                Output.TIMELINE: result.get("timeline", ""),
                Output.KEY_FINDINGS: result.get("key_findings", []),
            }
        )
