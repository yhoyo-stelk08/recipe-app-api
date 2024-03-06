"""
Test Custom Django Management Commands
"""

from unittest.mock import patch
from psycopg2 import OperationalError as pg_error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

@patch("core.management.commands.wait_for_db.Command.check")
class CommandTest(SimpleTestCase):
    """ Test Commands. """

    def test_wait_for_db_ready(self,patched_check):
        """ Test command to wait if database ready """
        patched_check.return_value = True
