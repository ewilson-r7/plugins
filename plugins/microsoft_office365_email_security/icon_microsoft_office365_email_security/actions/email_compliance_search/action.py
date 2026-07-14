import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException
from .schema import (
    EmailComplianceSearchInput,
    EmailComplianceSearchOutput,
    Input,
    Output,
    Component,
)

import json


class EmailComplianceSearch(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="email_compliance_search",
            description=Component.DESCRIPTION,
            input=EmailComplianceSearchInput(),
            output=EmailComplianceSearchOutput(),
        )

    def run(self, params={}):
        content_match_query = params.get(Input.CONTENT_MATCH_QUERY)
        self.logger.info(f"Searching mailboxes with query of: {content_match_query}")
        out, error = self.connection.client.email_compliance_search(
            params.get(Input.COMPLIANCE_SEARCH_NAME),
            content_match_query,
            params.get(Input.QUERY_TIMEOUT, 60),
            params.get(Input.EXCHANGE_LOCATION, "All"),
        )
        if isinstance(error, bytes):
            error = error.decode("utf-8")
        if isinstance(out, bytes):
            out = out.decode("utf-8")

        sources = self.extract_search_statistics(out, error)
        user_count = 0
        email_count = 0
        affected_users = []
        for item in sources:
            email_count += item["ContentItems"]
            if item["ContentItems"] > 0:
                affected_users.append(item["Name"])
            if item["ContentItems"] > 0:
                user_count += 1

        if error:
            self.logger.error(f"Error output received: \n{error}")
            if out:
                self.logger.error(f"Standard output received: \n{out}")
        else:
            self.logger.info(f"Search for {content_match_query} complete")

        return {
            Output.AFFECTED_USERS: user_count,
            Output.EMAILS_FOUND: email_count,
            Output.USERS: affected_users,
        }

    @staticmethod
    def extract_search_statistics(out, err):
        if "SearchStatistics" not in out:
            raise PluginException(
                cause="PowerShell returned an unexpected response.",
                assistance="Please check the error log for more information.",
                data=f"\n\nstdout:\n{out}\n\nstderr:\n{err}\n\n",
            )
        try:
            out_split = '{"SearchStatistics":' + str(out).split("@{SearchStatistics=")[1]
            search_statistics_info = out_split.split("\n")[0]
        except IndexError:
            raise PluginException(
                cause="Could not find SearchStatistics in compliance search results.",
                assistance="Please check the error log for more information.",
                data=f"\n\nstdout:\n{out}\n\nstderr:\n{err}\n\n",
            )
        try:
            out = json.loads(search_statistics_info)
        except json.decoder.JSONDecodeError:
            raise PluginException(
                preset=PluginException.Preset.INVALID_JSON,
                data=f"\n\nstdout:\n{out}\n\nstderr:\n{err}\n\n",
            )
        try:
            return_val = out["SearchStatistics"]["ExchangeBinding"]["Sources"]
        except KeyError:
            raise PluginException(
                cause="PowerShell returned an unexpected response.",
                assistance="Please check the error log for more information.",
                data=f"\n\nstdout:\n{out}\n\nstderr:\n{err}\n\n",
            )
        return return_val
