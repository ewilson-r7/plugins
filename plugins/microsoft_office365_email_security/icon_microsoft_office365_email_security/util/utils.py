import json

import validators
from insightconnect_plugin_runtime.exceptions import PluginException


class Utils:
    @staticmethod
    def extract_data(out: str) -> str:
        if "Success - trace follows:" in out:
            return out.split("Success - trace follows:")[1].replace("\n", "").replace("'", "")
        else:
            raise PluginException(
                cause="PowerShell returned an unexpected response.",
                assistance="Please ensure all of your input parameters are correct.",
                data=out,
            )

    @staticmethod
    def load_json(out: str, logger=None) -> list:
        try:
            return json.loads(out) if out is not None and out != "" else []
        except json.decoder.JSONDecodeError:
            err_index = out.find("Get-MessageTrace:")
            if err_index != -1 and logger:
                logger.error(out.split("Get-MessageTrace:")[1])
            raise PluginException(preset=PluginException.Preset.INVALID_JSON, data=out)

    @staticmethod
    def prepare_domain(domains: list) -> str:
        return ",".join([f'"{domain}"' for domain in domains])

    @staticmethod
    def validate_domains(domains: list):
        if not domains:
            raise PluginException(
                cause="List of domains is empty.",
                assistance="Please provide check the input and try again.",
            )
        for domain in domains:
            if not validators.domain(domain):
                raise PluginException(
                    cause=f"Wrong domain was provided. Incorrect domain: {domain}.",
                    assistance="Please provide a correct domain and try again.",
                )
