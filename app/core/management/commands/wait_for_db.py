"""

Django commands to wait for database to be available.

"""
import time

from psycopg2 import OperationalError as pg_op_error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django commands to wait for database """

    def handle(self, *args, **options):
        """Entry point for command."""
        self.stdout.write("Waiting for database...")
        db_up = False

        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except(pg_op_error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 seconds')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
