import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import ExplainScriptInput, ExplainScriptOutput, Input, Output, Component
from ...util.constants import EXPLAIN_SCRIPT_SYSTEM_PROMPT


class ExplainScript(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="explain_script",
            description=Component.DESCRIPTION,
            input=ExplainScriptInput(),
            output=ExplainScriptOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        context = params.get(Input.CONTEXT)
        script = params.get(Input.SCRIPT)
        script_type = params.get(Input.SCRIPT_TYPE)
        # END INPUT BINDING - DO NOT REMOVE

        script_type = script_type or "unknown"

        prompt_parts = [
            f"Analyze and explain the following {script_type} script/command:",
            f"```\n{script}\n```",
        ]

        if context:
            prompt_parts.append(f"Context where this was found: {context}")

        prompt_parts.append(
            "Provide a detailed explanation, risk assessment, MITRE ATT&CK techniques, "
            "and any IOCs found in the script."
        )

        prompt = "\n\n".join(prompt_parts)

        self.logger.info("Explaining %s script (%d characters)", script_type, len(script))

        result = self.connection.client.chat_completion_json(
            prompt=prompt,
            system_message=EXPLAIN_SCRIPT_SYSTEM_PROMPT,
            temperature=0.2,
        )

        return clean(
            {
                Output.EXPLANATION: result.get("explanation", ""),
                Output.RISK_LEVEL: result.get("risk_level", ""),
                Output.TECHNIQUES: result.get("techniques", []),
                Output.INDICATORS: result.get("indicators", []),
            }
        )
