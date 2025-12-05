import logging
from django.core.management.base import BaseCommand
from django.db import connection, transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'DELETES ALL TABLES in the current Django database. WARNING: Extremely destructive.'

    def add_arguments(self, parser):
        # Optional: Add a flag to bypass confirmation for automation/testing
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Bypass confirmation prompt (DANGER: use with extreme caution!).',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.ERROR("!! EXTREME WARNING: YOU ARE ABOUT TO DROP ALL DATABASE TABLES !!"))
        self.stdout.write(self.style.ERROR("This action will destroy all data AND schema definitions. It is irreversible."))

        if not options['no_input']:
            confirmation = input(
                self.style.ERROR(
                    "Type 'DROP ALL TABLES' exactly (case sensitive) to proceed: "
                )
            )
            if confirmation != 'DROP ALL TABLES':
                self.stdout.write(self.style.NOTICE("Table deletion cancelled by user."))
                return

        self.stdout.write(self.style.WARNING("Starting database table drop operation..."))

        try:
            # Tables that should generally be skipped if you want to keep
            # basic Django structure (e.g., if you only want to clear your app data)
            # However, for a full reset, dropping everything is the goal.
            # We keep the original logic, as it's the most aggressive way to clear the database.
            
            with connection.cursor() as cursor:
                # 1. Use Django's introspection to get the list of all table names
                table_names = connection.introspection.table_names()
                
                if not table_names:
                    self.stdout.write(self.style.WARNING("No tables found in the database. Nothing to drop."))
                    return

                # 2. Prepare and execute DROP TABLE statements
                dropped_count = 0
                for table_name in table_names:
                    # Executes DROP TABLE with CASCADE to handle foreign key dependencies 
                    # for better cross-database compatibility.
                    # Note: We must quote the table name to handle reserved keywords or mixed case
                    sql = f"DROP TABLE IF EXISTS {connection.ops.quote_name(table_name)} CASCADE;"
                    cursor.execute(sql)
                    self.stdout.write(f"  -> Dropped table: {table_name}")
                    dropped_count += 1
                
            self.stdout.write(self.style.SUCCESS(
                f"\nSuccessfully DROPPED {dropped_count} table(s) and all associated data."
            ))
            self.stdout.write(self.style.NOTICE("Run 'python manage.py migrate' to recreate the empty database schema."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"A critical error occurred during table deletion: {e}"))
            logger.error(f"Error executing drop_all_tables command: {e}")