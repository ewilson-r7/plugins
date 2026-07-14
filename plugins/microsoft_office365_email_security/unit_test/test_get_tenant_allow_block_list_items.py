import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_microsoft_office365_email_security.connection.connection import Connection
from icon_microsoft_office365_email_security.actions.get_tenant_allow_block_list_items import (
    GetTenantAllowBlockListItems,
)
import json
import logging


class TestGetTenantAllowBlockListItems(TestCase):
    def test_get_tenant_allow_block_list_items(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
