import csv
import logging
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from backend.rsvp_app.models import Guest

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Exports all guest data, including RSVP status, to a CSV file.'

    def handle(self, *args, **options):
        # Define the output file path in the project root
        project_root = settings.BASE_DIR
        file_name = 'guest_list_export.csv'
        output_path = os.path.join(project_root, file_name)

        self.stdout.write(self.style.WARNING(f"Starting CSV export to: {output_path}"))

        try:
            guests = Guest.objects.all().order_by('name')
            
            if not guests.exists():
                self.stdout.write(self.style.WARNING("No guests found to export."))
                return

            # Define the fields to include in the CSV
            fieldnames = [
                'name', 
                'phoneNumber', 
                'maxGuests',
                'response', 
                'attending_count', 
            ]

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write the header row
                writer.writeheader()
                
                # Write data rows
                for guest in guests:
                    row = {field: getattr(guest, field) for field in fieldnames}
                    writer.writerow(row)

            self.stdout.write(self.style.SUCCESS(
                f"Successfully exported {len(guests)} guests to {file_name}"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred during export: {e}"))
            logger.error(f"Error executing export_guests command: {e}")