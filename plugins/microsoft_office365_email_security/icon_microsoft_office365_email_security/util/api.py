import os
import subprocess  # noqa

from insightconnect_plugin_runtime.exceptions import PluginException

from icon_microsoft_office365_email_security.util.utils import Utils


class MicrosoftCommunicationAPI:
    def __init__(self, username, password, logger):
        self.username = username
        self.password = password
        self.logger = logger

    def get_list_blocked_domains(self):
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Get-HostedContentFilterPolicy.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
        ]
        return self.__run_powershell_script(args)

    def message_trace(self, start_date, end_date, sender):
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Trace.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
            "-EndDate",
            end_date,
            "-StartDate",
            start_date,
            "-Sender",
            sender,
        ]
        return self.__run_powershell_script(args)

    def block_sender_transport_rule(self, element_to_block, transport_rule_name):
        if element_to_block:
            element_to_block = element_to_block.strip()
        if transport_rule_name:
            transport_rule_name = transport_rule_name.strip()

        self.logger.info(f"Blocking: {element_to_block}")
        self.logger.info(f"With transport rule: {transport_rule_name}")

        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Transport-Rules.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
            "-EmailOrDomainToBlock",
            element_to_block,
            "-RuleName",
            transport_rule_name,
        ]
        return self.__run_powershell_script(args)

    def email_compliance_search(self, compliance_search_name, content_match_query, timeout, exchange_location):
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Search.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
            "-ComplianceSearchName",
            self.__remove_invalid_characters(compliance_search_name),
            "-ContentMatchQuery",
            self.__unescape_content_match_query(content_match_query),
            "-TimeoutInMinutes",
            str(timeout),
            "-ExchangeLocation",
            exchange_location,
        ]
        return self.__run_powershell_script(args, True)

    def mass_purge(self, compliance_search_name, timeout):
        self.logger.info(f"Attempting to delete results of compliance search: {compliance_search_name}")
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Mass-Purge.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
            "-ComplianceSearchName",
            compliance_search_name,
            "-TimeoutInMinutes",
            str(timeout),
            "-Office365URI",
        ]
        return self.__run_powershell_script(args)

    def mass_search_and_purge(self, compliance_search_name, content_match_query, timeout, delete_items):
        self.logger.info(f"Searching mailboxes with query of: {content_match_query}")
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Mass-Search-And-Purge.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
            "-ComplianceSearchName",
            compliance_search_name,
            "-ContentMatchQuery",
            self.__unescape_content_match_query(content_match_query),
            "-TimeoutInMinutes",
            str(timeout),
            "-DeleteItems",
            str(delete_items),
        ]
        return self.__run_powershell_script(args, True)

    def update_blocked_list(self, operation, search_filter, domains):
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Update-blocked-list-domain.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
            "-SearchFilter",
            search_filter,
            "-Action",
            operation,
            "-Domains",
            Utils.prepare_domain(domains),
        ]
        return self.__run_powershell_script(args)

    def test_connection(self):
        self.logger.info("Connecting to ExchangeOnline")
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Connection-Test.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
        ]
        return self.__run_powershell_script(args)

    def get_tenant_allow_block_list_items(self, list_type, action_type=None):
        self.logger.info(f"Getting Tenant Allow/Block List items for ListType: {list_type}")
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Get-TenantAllowBlockListItems.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
            "-ListType",
            list_type,
        ]
        if action_type:
            args.extend(["-ActionType", action_type])
        return self.__run_powershell_script(args)

    def create_tenant_allow_block_list_entry(
        self, list_type, entries, action_type, no_expiration=False, expiration_days=30, notes=""
    ):
        self.logger.info(f"Creating Tenant Allow/Block List entry: {action_type} {list_type} - {entries}")
        entries_str = ",".join(entries)
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/New-TenantAllowBlockListItems.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
            "-ListType",
            list_type,
            "-Entries",
            entries_str,
            "-ActionType",
            action_type,
            "-NoExpiration",
            str(no_expiration).lower(),
            "-ExpirationDays",
            str(expiration_days),
        ]
        if notes:
            args.extend(["-Notes", notes])
        return self.__run_powershell_script(args)

    def remove_tenant_allow_block_list_entry(self, list_type, entries):
        self.logger.info(f"Removing Tenant Allow/Block List entries: {list_type} - {entries}")
        entries_str = ",".join(entries)
        args = [
            "pwsh",
            "-ExecutionPolicy",
            "Unrestricted",
            "-File",
            "icon_microsoft_office365_email_security/powershell/Remove-TenantAllowBlockListItems.ps1",
            "-Username",
            self.username,
            "-Password",
            self.password,
            "-ListType",
            list_type,
            "-Entries",
            entries_str,
        ]
        return self.__run_powershell_script(args)

    def __remove_invalid_characters(self, input_compliance_search_name: str) -> str:
        """
        Remove invalid characters from the input compliance search name.

        :param input_compliance_search_name: The input compliance search name.
        :type: str

        :return: The cleaned compliance search name without invalid characters.
        :rtype: str
        """

        invalid_characters = ("'", '"', "*", "?", "<", ">")
        output_compliance_search_name = input_compliance_search_name
        for invalid_character in invalid_characters:
            output_compliance_search_name = output_compliance_search_name.replace(invalid_character, "")
        self.logger.info(f"Removed characters: {output_compliance_search_name}")
        return output_compliance_search_name

    def __unescape_content_match_query(self, query: str) -> str:
        """
        Remove backslash escape characters that may be injected before quotation marks
        by the InsightConnect API when passing values between workflow steps.

        :param query: The raw content match query string.
        :type: str

        :return: The query with backslash-escaped quotes replaced by plain quotes.
        :rtype: str
        """
        unescaped = query.replace('\\"', '"')
        self.logger.info(f"Content match query after unescape: {unescaped}")
        return unescaped

    def __run_powershell_script(self, args, universal_newlines=False):
        if universal_newlines:
            try:
                powershell = subprocess.Popen(  # noqa
                    args,
                    cwd=os.getcwd(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=universal_newlines,
                )
            except Exception as error:
                raise PluginException(
                    cause="While executing a child program in a new process exception appears.",
                    assistance="Please see the plugin logs for more information.",
                    data=error,
                )
        else:
            try:
                powershell = subprocess.Popen(  # noqa
                    args,
                    cwd=os.getcwd(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except Exception as error:
                raise PluginException(
                    cause="While executing a child program in a new process exception appears.",
                    assistance="Please see the plugin logs for more information.",
                    data=error,
                )
        return powershell.communicate()
