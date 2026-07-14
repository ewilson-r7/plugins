import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_microsoft_office365_email_security.connection.connection import Connection
from icon_microsoft_office365_email_security.actions.create_tenant_allow_block_list_entry import (
    CreateTenantAllowBlockListEntry,
)
import json
import logging


class TestCreateTenantAllowBlockListEntry(TestCase):
    def test_create_tenant_allow_block_list_entry(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
