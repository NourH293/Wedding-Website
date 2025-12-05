import logging
from django.core.management.base import BaseCommand
from backend.rsvp_app.models import Guest # Adjust this import based on your actual structure

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clears the RSVP response and attending count for all guests in the database.'

    def handle(self, *args, **options):
        # Set a default value for response (e.g., 'Pending')
        DEFAULT_RESPONSE = 'Pending'
        # Set a default value for attending_count (e.g., 0 or None)
        # Using 0 as the default if a guest has not responded.
        DEFAULT_COUNT = 0 

        self.stdout.write(self.style.WARNING("Starting to reset all guest RSVP responses..."))
        
        try:
            # Update all Guest objects at once
            updated_count = Guest.objects.all().update(
                response=DEFAULT_RESPONSE,
                attending_count=DEFAULT_COUNT
            )

            if updated_count > 0:
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully reset RSVP for {updated_count} guests."
                ))
            else:
                self.stdout.write(self.style.WARNING("No guests found in the database to reset."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred during reset: {e}"))
            logger.error(f"Error executing clear_responses command: {e}")