import logging
from django.core.management.base import BaseCommand
from backend.rsvp_app.models import Guest
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'DELETES ALL guest records from the database. Requires confirmation.'

    def add_arguments(self, parser):
        # Optional: Add a flag to bypass confirmation for automation/testing
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Bypass confirmation prompt (DANGER: use with caution in production!).',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.ERROR("!! WARNING: DELETION COMMAND INITIATED !!"))
        
        # 1. Get the current count
        initial_count = Guest.objects.count()
        
        if initial_count == 0:
            self.stdout.write(self.style.WARNING("No guests found in the database. Nothing to delete."))
            return

        self.stdout.write(f"Found {initial_count} guest records.")

        # 2. Confirmation Prompt
        if not options['no_input']:
            confirmation = input(
                self.style.ERROR(
                    "Are you absolutely sure you want to DELETE ALL guest records? "
                    "This action is irreversible. Type 'yes' to proceed: "
                )
            )
            if confirmation.lower() != 'yes':
                self.stdout.write(self.style.NOTICE("Deletion cancelled by user."))
                return

        # 3. Perform Deletion
        self.stdout.write(self.style.WARNING("Starting mass deletion..."))
        try:
            with transaction.atomic():
                # The delete() method executes the deletion immediately
                deleted_count, _ = Guest.objects.all().delete()

            if deleted_count > 0:
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully DELETED {deleted_count} guest records."
                ))
            else:
                # Should not happen if initial_count > 0, but good for robustness
                self.stdout.write(self.style.WARNING("No guests were deleted."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred during deletion: {e}"))
            logger.error(f"Error executing delete_all_guests command: {e}")