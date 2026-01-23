from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

import os
import sys
from django.core.exceptions import ImproperlyConfigured

# Expected environment: local | test | live
# Default to 'local' when not provided to keep developer
# experience smooth.
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local").lower()
# Convenience flags for app logic
IS_TEST = ENVIRONMENT == "test"
IS_LIVE = ENVIRONMENT == "live"


# ============================================================
# SECURITY
# ============================================================

# NOTE: Do NOT change SECRET_KEY, DEBUG, or ALLOWED_HOSTS in this
# reconciled file — they are preserved from the original source.
SECRET_KEY = "dev-secret-key-change-me-in-prod"
DEBUG = True

ALLOWED_HOSTS = ["*"]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Auth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # CKEditor 5 (rich text for blog admin)
    "django_ckeditor_5",

    # Project apps
    "home",
    "blog.apps.BlogConfig",
    "mediahub",
    "collections_app",
    "shop.apps.ShopConfig",
    "contact",
    "story",
    "users",
    # Image thumbnailing
    "sorl.thumbnail",
    # Commercials (added in stash)
    "commercials",
    # Payments integration (guarded/test-aware)
    "payments",
]

SITE_ID = 1


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    "allauth.account.middleware.AccountMiddleware",
]


# ============================================================
# URLS / WSGI
# ============================================================

ROOT_URLCONF = "ochre.urls"
WSGI_APPLICATION = "ochre.wsgi.application"


# ============================================================
# TEMPLATES  ✅ FIXED
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",   # REQUIRED
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Shop
                "shop.context_processors.cart_count",
                # Provide site-wide contact email from settings
                "ochre.context_processors.contact_email",
                # Global feature flags for templates
                "ochre.context_processors.global_feature_flags",
            ],
        },
    }
]


# ============================================================
# DATABASE
# ============================================================

# Default to SQLite so local/test run without extra config.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Optional: if a DATABASE_URL is provided, configure PostgreSQL.
# This keeps SQLite as the default and only activates Postgres when
# an explicit DATABASE_URL (or POSTGRES_* env vars) is present.
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL:
    # Minimal parsing of DATABASE_URL (postgres://user:pass@host:port/dbname)
    from urllib.parse import urlparse

    parsed = urlparse(DATABASE_URL)
    if parsed.scheme.startswith("postgres"):
        POSTGRES_DB = (parsed.path or "").lstrip("/")
        POSTGRES_USER = parsed.username
        POSTGRES_PASSWORD = parsed.password
        POSTGRES_HOST = parsed.hostname
        POSTGRES_PORT = parsed.port or os.environ.get("POSTGRES_PORT", "5432")

        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": POSTGRES_DB,
                "USER": POSTGRES_USER,
                "PASSWORD": POSTGRES_PASSWORD,
                "HOST": POSTGRES_HOST,
                "PORT": POSTGRES_PORT,
            }
        }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# ============================================================
# STATIC & MEDIA DEPLOYMENT
#
# Local development: keep media under BASE_DIR/media
# Test / Production: nginx serves from /var/www/ochre
# The ENVIRONMENT env var controls the switch (local|test|live|production)
# ============================================================

import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

MEDIA_URL = "/media/"

if ENVIRONMENT in ("test", "live", "production"):
    STATIC_ROOT = "/var/www/ochre/static"
    MEDIA_ROOT = "/var/www/ochre/media"
else:
    STATIC_ROOT = BASE_DIR / "staticfiles"
    MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# MEDIA FILES  ✅ CRITICAL FOR BLOG IMAGES
# ============================================================

# MEDIA_URL and MEDIA_ROOT are configured above according to ENVIRONMENT

# TinyMCE Cloud API key - read from environment. Set this in production.
TINYMCE_API_KEY = os.environ.get('TINYMCE_API_KEY', "")

# CKEditor5 upload path (relative to MEDIA_ROOT)
CKEDITOR5_UPLOAD_PATH = "ckeditor5/"

# CKEditor5 configuration: use Base64 image embedding only and toolbar
CKEDITOR5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "|",
            "sourceEditing",
            "undo",
            "redo",
        ],
        "heading": {
            "options": [
                {"model": "paragraph", "title": "Paragraph"},
                {"model": "heading2", "view": "h2", "title": "Heading 2"},
                {"model": "heading3", "view": "h3", "title": "Heading 3"},
            ]
        },
    }
}

# Named config for blog admin (explicit full toolbar)
CKEDITOR5_CONFIGS["blog"] = {
    "toolbar": [
        "heading",
        "bold",
        "italic",
        "underline",
        "link",
        "bulletedList",
        "numberedList",
        "blockQuote",
        "insertImage",
        "undo",
        "redo",
    ],
}

# Backwards-compatible alias: some versions of `django_ckeditor_5` look for
# `CKEDITOR_5_CONFIGS` (with an underscore). Define it here to ensure both
# variants are available without modifying site-packages.
CKEDITOR_5_CONFIGS = CKEDITOR5_CONFIGS


# ============================================================
# AUTH / ALLAUTH
# ============================================================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["username", "email", "password1", "password2"]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Configure social account providers (Google OAuth2)
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # DB-backed SocialApp is authoritative.
        # Do NOT define APP here.
    }
}

# When True, visiting a social login URL via GET will immediately
# redirect to the provider (avoids the intermediate confirmation page).
SOCIALACCOUNT_LOGIN_ON_GET = True


# Feature flags and external integrations readiness (credential-ready)
# Do not hardcode secrets; use env vars with empty-string fallback.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_OAUTH_CONFIGURED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

# OTP provider (placeholder API key expected)
OTP_PROVIDER_BACKEND = os.getenv('OTP_PROVIDER_BACKEND', '')
OTP_PROVIDER_API_KEY = os.environ.get("OTP_PROVIDER_API_KEY", "")
OTP_PROVIDER_CONFIGURED = bool(OTP_PROVIDER_BACKEND or OTP_PROVIDER_API_KEY)

# SMTP / Email readiness (no live-only exceptions here; just flags)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_CONFIGURED = bool(EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)

# NOTE: SMTP is intentionally pending due to DNS/DLT delays for this deployment.
# Email sending is guarded by `EMAIL_CONFIGURED` — the codebase will not fail
# when SMTP is not configured; email hooks are non-blocking and logged.

# Razorpay keys: read from env, expose a boolean indicating if test keys provided
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_TEST_KEYS_PROVIDED = bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET)

# MSG91 (OTP) placeholders
MSG91_AUTH_KEY = os.environ.get("MSG91_AUTH_KEY", "")
MSG91_SENDER_ID = os.environ.get("MSG91_SENDER_ID", "")
MSG91_TEMPLATE_ID = os.environ.get("MSG91_TEMPLATE_ID", "")
# NOTE: SMS (MSG91) integration is intentionally pending; hooks are stubs/logged.

# Analytics / pixels
GOOGLE_ANALYTICS_ID = os.environ.get("GOOGLE_ANALYTICS_ID", "")
META_PIXEL_ID = os.environ.get("META_PIXEL_ID", "")


# ============================================================
# DEFAULTS
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Contact configuration (single point of truth for contact email)
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "contact@domain.com")
