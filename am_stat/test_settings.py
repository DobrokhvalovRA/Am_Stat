"""
Test settings for Am_stat project.
Uses SQLite instead of PostgreSQL for faster testing without database setup.
"""
from am_stat.settings import *

# Use SQLite for tests instead of PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# Optional: uncomment to disable migrations during tests for speed
# MIGRATION_MODULES = DisableMigrations()

# Make password hashing faster for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable debug toolbar and other debug tools in tests
DEBUG = False
