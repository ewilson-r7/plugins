import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_microsoft_office365_email_security.connection.connection import Connection
from icon_microsoft_office365_email_security.actions.remove_tenant_allow_block_list_entry import (
    RemoveTenantAllowBlockListEntry,
)
import json
import logging


class TestRemoveTenantAllowBlockListEntry(TestCase):
    def test_remove_tenant_allow_block_list_entry(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
