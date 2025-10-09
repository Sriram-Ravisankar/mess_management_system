import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-m_k#+n^j7!s(g#@3r7j6g5h4f3e2d1c0b9a8z' # REPLACE THIS WITH A REAL SECRET KEY!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 3rd party apps
    # 'tailwind', # Optional if using full Tailwind workflow
    
    # My Apps
    'mess_app', # <--- MY APPLICATION
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mess_management_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mess_management_project.wsgi.application'


# Database
# Using SQLite as requested
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# ... (default validation settings)


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' # Adjust to your local timezone
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static", # Look for static files in the root 'static' folder
]


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Custom Project Settings ---

# 1. Custom User Model for RBAC
AUTH_USER_MODEL = 'mess_app.User'

# 2. Login/Logout Redirects
# The URL path to redirect to when a user must log in.
# Your urls.py defines the login path as 'login/'.
LOGIN_URL = '/login/'
# If you also want to redirect to the student dashboard after a successful login:
LOGIN_REDIRECT_URL = '/student-dashboard/'
# LOGIN_REDIRECT_URL = '/student-dashboard/'
# LOGOUT_REDIRECT_URL = '/login/' 

# 3. Twilio Settings (REPLACE WITH YOUR ACTUAL CREDENTIALS)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'your_auth_token_here')
# Use the Twilio Sandbox WhatsApp number or your approved number
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')


# --- Session Control Settings (FIX FOR RE-LOGIN ON REFRESH) ---

# Set to False to prevent session from expiring when the browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False 

# Set the age of the session cookie (in seconds). (1 week)
SESSION_COOKIE_AGE = 604800 

# Ensure the cookie is accessible by JavaScript only (security best practice)
SESSION_COOKIE_HTTPONLY = True 

# <--- FIX: Explicitly set cookie security settings to False for local HTTP development -->
SESSION_COOKIE_SECURE = False 
CSRF_COOKIE_SECURE = False 

# Ensure cookies work reliably on http://127.0.0.1
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
# AGGRESSIVE FIX: Ensure the cookie is correctly issued for the local environment
SESSION_COOKIE_DOMAIN = None