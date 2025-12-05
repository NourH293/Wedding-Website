#! /bin/bash
#python manage.py drop_all_tables --no-input
python manage.py makemigrations rsvp_app
python manage.py migrate
python manage.py delete_all_guests --no-input
python manage.py load_initial_data
python manage.py runserver 0.0.0.0:8000
python manage.py export_guests