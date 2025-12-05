import json
import os
import pandas as pd
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from backend.rsvp_app.models import Guest 

class Command(BaseCommand):
    """
    A custom management command to load initial guest data from a JSON file
    into the database, ensuring unique phoneNumber and preventing duplicates.
    """
    help = 'Loads initial guest data from initialGuests.json'

    def handle(self, *args, **options):
        # 1. Get the path to the JSON file from Django settings
        data_file_path = getattr(settings, 'INITIAL_GUEST_DATA_PATH', None)
        
        if not data_file_path or not Path(data_file_path).exists():
            self.stderr.write(self.style.ERROR(f"Initial data file not found at: {data_file_path}"))
            return

        self.stdout.write(f"Attempting to load data from: {data_file_path}")
        
        try:
            with open(data_file_path, 'r') as f:
                data = pd.read_csv(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred while reading the file: {e}"))
            return

        total_created = 0
        total_skipped = 0

        # Use a transaction to ensure either all data is saved, or none is.
        with transaction.atomic():
            for index, item in data.iterrows():
                try:
                    # Check if a Guest with this phoneNumber already exists
                    if Guest.objects.filter(phoneNumber=item['phoneNumber']).exists():
                        self.stdout.write(self.style.WARNING(f"Guest with phoneNumber {item['phoneNumber']} ('{item['name']}') already exists. Skipping."))
                        total_skipped += 1
                        continue

                    # FIX: Updated keyword arguments to match likely model field names.
                    # IMPORTANT: You MUST verify and change these to match the exact field names 
                    # in your backend/rsvp_app/models.py file.
                    Guest.objects.create(
                        name=item['name'],
                        phoneNumber=item['phoneNumber'],
                        maxGuests=item.get('maxGuests', 1),
                        response=item.get('response', 'Pending'),
                        attending_count=item.get('attending_count', 0),
                    )
                    total_created += 1
                except Exception as e:
                    # Capture the specific error for better debugging next time
                    self.stderr.write(self.style.ERROR(f"Failed to create guest '{item.get('name', 'N/A')}' (Phone Number: {item.get('phoneNumber', 'N/A')}): {e}"))
                    # The transaction will automatically roll back if an exception is raised here

        if total_created > 0:
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {total_created} new guests."))
        if total_skipped > 0:
            self.stdout.write(self.style.WARNING(f"Skipped {total_skipped} guests that already existed."))