import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import SuggestResponseActionsInput, SuggestResponseActionsOutput, Input, Output, Component
from ...util.constants import SUGGEST_RESPONSE_SYSTEM_PROMPT


class SuggestResponseActions(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="suggest_response_actions",
            description=Component.DESCRIPTION,
            input=SuggestResponseActionsInput(),
            output=SuggestResponseActionsOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        environment_context = params.get(Input.ENVIRONMENT_CONTEXT)
        incident_description = params.get(Input.INCIDENT_DESCRIPTION)
        response_phase = params.get(Input.RESPONSE_PHASE)
        # END INPUT BINDING - DO NOT REMOVE

        response_phase = response_phase or "containment"

        prompt_parts = [
            "Provide incident response recommendations for the following security incident.",
            f"Current response phase: {response_phase}",
            f"Incident description:\n{incident_description}",
        ]

        if environment_context:
            prompt_parts.append(f"Environment context:\n{environment_context}")

        prompt_parts.append(
            "Provide prioritized immediate actions, investigation steps, and long-term recommendations."
        )

        prompt = "\n\n".join(prompt_parts)

        self.logger.info("Generating response recommendations (phase: %s)", response_phase)

        result = self.connection.client.chat_completion_json(
            prompt=prompt,
            system_message=SUGGEST_RESPONSE_SYSTEM_PROMPT,
            temperature=0.3,
        )

        return clean(
            {
                Output.IMMEDIATE_ACTIONS: result.get("immediate_actions", []),
                Output.INVESTIGATION_STEPS: result.get("investigation_steps", []),
                Output.LONG_TERM_RECOMMENDATIONS: result.get("long_term_recommendations", []),
            }
        )
