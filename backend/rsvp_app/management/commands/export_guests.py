import csv
import logging
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from backend.rsvp_app.models import Guest

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Exports all guest data, merging with existing CSV and preserving non-database entries.'

    def handle(self, *args, **options):
        # Define the output file path
        project_root = settings.BASE_DIR
        file_name = 'guest_list_export.csv'
        output_path = os.path.join(project_root, file_name)
        
        # NOTE: For robust merging, consider adding the primary key (pk) of Guest 
        # to fieldnames and using it as the MERGE_KEY. For now, we'll use 'name'.
        MERGE_KEY = 'phoneNumber'
        
        fieldnames = [
            'name',
            MERGE_KEY, 
            'maxGuests',
            'response', 
            'attending_count', 
        ]

        self.stdout.write(self.style.WARNING(f"Starting CSV export merge to: {output_path}"))

        try:
            # 1. READ EXISTING CSV DATA (if it exists)
            csv_data = {}
            if os.path.exists(output_path):
                with open(output_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Read existing rows into a dictionary, keyed by the merge key
                    for row in reader:
                        # Only include rows that have the merge key
                        if row.get(MERGE_KEY):
                            csv_data[row[MERGE_KEY]] = row
                        
                self.stdout.write(self.style.NOTICE(f"Read {len(csv_data)} existing rows from CSV."))

            # 2. GET ALL DATABASE DATA
            guests = Guest.objects.all()
            if not guests.exists():
                self.stdout.write(self.style.WARNING("No guests found in database to export or merge."))
                # If no guests, we still need to write the existing CSV data back
                # to maintain its state, unless the file didn't exist, in which
                # case we exit.
                if not csv_data:
                    return

            # 3. MERGE DATABASE DATA INTO CSV DATA
            updated_count = 0
            new_count = 0
            
            for guest in guests:
                # Prepare the row from the database object
                db_row = {field: getattr(guest, field) for field in fieldnames}
                
                key = db_row[MERGE_KEY]
                
                if key in csv_data:
                    # Update: Replace the existing CSV row with the fresh DB data
                    # This ensures modifications in the DB are reflected.
                    csv_data[key].update(db_row)
                    updated_count += 1
                else:
                    # Add: The database entry is new
                    csv_data[key] = db_row
                    new_count += 1
            
            # The final data to write is the values of the csv_data dictionary
            final_rows = list(csv_data.values())

            # 4. WRITE THE COMPLETE, MERGED DATA BACK TO THE CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Ensure the header is based on the defined fieldnames
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames) 
                
                # Write the header row
                writer.writeheader() 
                
                # Write all final rows
                writer.writerows(final_rows) 

            self.stdout.write(self.style.SUCCESS(
                f"Successfully completed merge export to {file_name}."
            ))
            self.stdout.write(self.style.SUCCESS(
                f"Summary: {len(final_rows)} total rows | {new_count} added | {updated_count} updated | {len(final_rows) - new_count - updated_count} preserved"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred during export: {e}"))
            logger.error(f"Error executing export_guests command: {e}")