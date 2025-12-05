# Django settings for a self-hosted RSVP API.

import os
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE SECURITY SETTINGS ---
# IMPORTANT: Replace with a secret key generated for production!
SECRET_KEY = 'django-insecure-x+5%9k1+*0%@*o65j@7*!9y8q12x9a-x-v8h(3%g_r25t*k*i='

DEBUG = True # Set to False in production

ALLOWED_HOSTS = ['*'] # Restrict this to your domain in production

# --- CORS Configuration (Important for Vue frontend) ---
# Allows the Vue frontend (running on a different port/domain) to talk to Django.
CORS_ALLOW_ALL_ORIGINS = True

# --- Application Definitions ---

INSTALLED_APPS = [
    # Required core apps:
    'django.contrib.auth',           # <--- ADDED: Necessary for Permissions and Auth
    'django.contrib.contenttypes', 
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders', 
    'rest_framework', 
    'backend.rsvp_app', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Must be highly placed
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

WSGI_APPLICATION = 'backend.wsgi.application'

# --- Database Configuration ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # Switched to legacy 'postgresql' engine name
        'NAME': 'rsvp_db',           
        'USER': 'rsvp_user',         
        'PASSWORD': 'MySecretRsvpPassword123',
        'HOST': 'localhost',         
        'PORT': '5432',              
    }
}


# --- API Configuration ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', 
    ]
}

# --- Time Zone ---
TIME_ZONE = 'UTC'
USE_TZ = True


# --- Static Files (Not strictly needed for API, but good practice) ---
STATIC_URL = 'static/'

# --- Custom App Configurations ---
INITIAL_GUEST_DATA_PATH = BASE_DIR / 'guest_list_export.csv'