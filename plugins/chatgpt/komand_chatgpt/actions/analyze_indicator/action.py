import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import AnalyzeIndicatorInput, AnalyzeIndicatorOutput, Input, Output, Component
from ...util.constants import ANALYZE_INDICATOR_SYSTEM_PROMPT


class AnalyzeIndicator(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="analyze_indicator",
            description=Component.DESCRIPTION,
            input=AnalyzeIndicatorInput(),
            output=AnalyzeIndicatorOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        additional_context = params.get(Input.ADDITIONAL_CONTEXT)
        indicator = params.get(Input.INDICATOR)
        indicator_type = params.get(Input.INDICATOR_TYPE)
        # END INPUT BINDING - DO NOT REMOVE

        prompt_parts = [
            f"Analyze the following {indicator_type.replace('_', ' ')} indicator of compromise:",
            f"Indicator: {indicator}",
        ]

        if additional_context:
            prompt_parts.append(f"Additional context: {additional_context}")

        prompt_parts.append(
            "Provide a detailed threat analysis, risk assessment, and recommended response actions."
        )

        prompt = "\n\n".join(prompt_parts)

        self.logger.info("Analyzing %s indicator: %s", indicator_type, indicator)

        result = self.connection.client.chat_completion_json(
            prompt=prompt,
            system_message=ANALYZE_INDICATOR_SYSTEM_PROMPT,
            temperature=0.3,
        )

        return clean(
            {
                Output.ANALYSIS: result.get("analysis", ""),
                Output.RISK_ASSESSMENT: result.get("risk_assessment", ""),
                Output.RECOMMENDED_ACTIONS: result.get("recommended_actions", []),
            }
        )
