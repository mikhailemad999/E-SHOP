"""
Local development settings.
"""

from config.settings import *  # noqa: F401, F403

# ─── Debug ───────────────────────────────────────────────────────
DEBUG = True

# ─── Debug Toolbar ───────────────────────────────────────────────
INSTALLED_APPS += ["debug_toolbar", "django_extensions"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# ─── Email (console backend for dev) ─────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ─── Storage (local filesystem for dev) ──────────────────────────
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
