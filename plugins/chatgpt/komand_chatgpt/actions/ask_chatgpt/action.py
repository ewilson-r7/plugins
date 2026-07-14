import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import AskChatgptInput, AskChatgptOutput, Input, Output, Component
from ...util.constants import DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE


class AskChatgpt(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="ask_chatgpt", description=Component.DESCRIPTION, input=AskChatgptInput(), output=AskChatgptOutput()
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        max_tokens = params.get(Input.MAX_TOKENS)
        prompt = params.get(Input.PROMPT)
        system_message = params.get(Input.SYSTEM_MESSAGE)
        temperature = params.get(Input.TEMPERATURE)
        # END INPUT BINDING - DO NOT REMOVE

        max_tokens = max_tokens or DEFAULT_MAX_TOKENS
        temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE

        self.logger.info("Sending prompt to ChatGPT (max_tokens=%d, temperature=%s)", max_tokens, temperature)

        result = self.connection.client.chat_completion(
            prompt=prompt,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return clean(
            {
                Output.RESPONSE: result["response"],
                Output.USAGE: result["usage"],
            }
        )
