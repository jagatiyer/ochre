from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
import os
import sys
from django.core.exceptions import ImproperlyConfigured

# Expected environment: local | test | live
# Default to 'local' when not provided to keep developer experience smooth.
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local").lower()

# Require a virtualenv to be active for safety. This is an early, explicit guard
# to prevent accidental use of global/site Python and to satisfy project policy.
if not (os.environ.get("VIRTUAL_ENV") or os.environ.get("PYENV_VIRTUAL_ENV") or getattr(sys, "base_prefix", None) != getattr(sys, "prefix", None)):
    raise ImproperlyConfigured(
        "A Python virtualenv must be active. Activate your virtualenv before running Django."
    )

# Validate ENVIRONMENT value
if ENVIRONMENT not in ("local", "test", "live"):
    raise ImproperlyConfigured(f"ENVIRONMENT must be one of local,test,live (got {ENVIRONMENT!r})")

# Convenience flags for app logic
IS_TEST = ENVIRONMENT == "test"
IS_LIVE = ENVIRONMENT == "live"

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

# Additional strictness for live environment: fail fast when required secrets/configs missing.
if ENVIRONMENT == "live":
    # SECRET_KEY must be set (don't allow the dev placeholder in production)
    if os.environ.get("SECRET_KEY"):
        SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY or SECRET_KEY == "dev-secret-key-change-me-in-prod":
        raise ImproperlyConfigured("SECRET_KEY must be set to a secure value in the live environment.")

    # Require PostgreSQL config to be provided via env vars (live must not use sqlite)
    if not any(os.environ.get(k) for k in ("DATABASE_URL", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD")):
        raise ImproperlyConfigured(
            "Live environment requires PostgreSQL configuration (set DATABASE_URL or POSTGRES_* env vars)."
        )


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
    "commercials",
    "shop.apps.ShopConfig",
    "contact",
    "story",
    "users",
    # Image thumbnailing
    "sorl.thumbnail",
<<<<<<< Updated upstream
    # Commercials (added in stash)
    "commercials",
    # Payments integration (guarded/test-aware)
=======
    # Payments (Razorpay test integration)
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
                # Global feature flags for templates
=======
                # Global feature flags for templates (analytics, payments, oauth)
>>>>>>> Stashed changes
                "ochre.context_processors.global_feature_flags",
            ],
        },
    }
]


# ============================================================
# DATABASE
# ============================================================

<<<<<<< Updated upstream
# Default to SQLite so local/test run without extra config.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
=======
# Select database backend by ENVIRONMENT
if ENVIRONMENT in ("local", "test"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # live environment: require and use PostgreSQL
    # Support either explicit POSTGRES_* env vars or a DATABASE_URL
    DATABASE_URL = os.environ.get("DATABASE_URL")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT") or "5432"

    if DATABASE_URL and not (POSTGRES_DB and POSTGRES_USER and POSTGRES_PASSWORD):
        # Minimal DATABASE_URL parsing (postgres://user:pass@host:port/dbname)
        from urllib.parse import urlparse

        parsed = urlparse(DATABASE_URL)
        if parsed.scheme.startswith("postgres"):
            POSTGRES_DB = (parsed.path or "").lstrip("/")
            POSTGRES_USER = parsed.username
            POSTGRES_PASSWORD = parsed.password
            POSTGRES_HOST = parsed.hostname
            POSTGRES_PORT = parsed.port or POSTGRES_PORT

    if not (POSTGRES_DB and POSTGRES_USER and POSTGRES_PASSWORD and POSTGRES_HOST):
        raise ImproperlyConfigured(
            "Live environment requires PostgreSQL connection via POSTGRES_* env vars or a valid DATABASE_URL."
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": POSTGRES_DB,
            "USER": POSTGRES_USER,
            "PASSWORD": POSTGRES_PASSWORD,
            "HOST": POSTGRES_HOST,
            "PORT": POSTGRES_PORT,
        }
>>>>>>> Stashed changes
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
STATIC_ROOT = BASE_DIR / "staticfiles"

# For local and test environments use the simple staticfiles storage so
# `collectstatic` is not required to serve static assets under runserver.
if ENVIRONMENT in ("local", "test"):
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"


# ============================================================
# MEDIA FILES  ✅ CRITICAL FOR BLOG IMAGES
# ============================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

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


<<<<<<< Updated upstream
=======
# --------------------------------------------------
# Razorpay keys: require real secrets in live, allow test placeholders in local/test
# --------------------------------------------------
if ENVIRONMENT == "live":
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
    if not (RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET):
        raise ImproperlyConfigured(
            "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be set in the live environment."
        )
    # In live we expect production (non-test) keys
    RAZORPAY_TEST_KEYS_PROVIDED = False
else:
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID") or "rzp_test_PLACEHOLDER"
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET") or "rzp_test_SECRET_PLACEHOLDER"
    RAZORPAY_TEST_KEYS_PROVIDED = bool(os.getenv("RAZORPAY_KEY_ID") and os.getenv("RAZORPAY_KEY_SECRET"))

# --------------------------------------------------
# Google OAuth flags (django-allauth)
# --------------------------------------------------
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_OAUTH_CONFIGURED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

# --------------------------------------------------
# OTP provider flag
# Provide an environment variable `OTP_PROVIDER_BACKEND` which should be a
# dotted path to a backend class implementing `send_otp(phone)` and
# `verify_otp(phone, code, request_id)`.
# Fallback: Dummy provider is used when unset (dev-only).
# --------------------------------------------------
OTP_PROVIDER_BACKEND = os.getenv('OTP_PROVIDER_BACKEND', '')
OTP_PROVIDER_CONFIGURED = bool(OTP_PROVIDER_BACKEND or os.getenv('OTP_PROVIDER_API_KEY'))

# --------------------------------------------------
# Email readiness
# --------------------------------------------------
EMAIL_CONFIGURED = bool(os.getenv('EMAIL_HOST') and os.getenv('EMAIL_HOST_USER') and os.getenv('EMAIL_HOST_PASSWORD'))

>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
# When True, visiting a social login URL via GET will immediately
# redirect to the provider (avoids the intermediate confirmation page).
SOCIALACCOUNT_LOGIN_ON_GET = True


# Feature flags and external integrations readiness (credential-ready)
# Do not hardcode secrets; use env vars with empty-string fallback.
=======
# Feature flags and external integrations readiness
>>>>>>> Stashed changes
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_OAUTH_CONFIGURED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

# OTP provider (placeholder API key expected)
<<<<<<< Updated upstream
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
=======
OTP_PROVIDER_API_KEY = os.environ.get("OTP_PROVIDER_API_KEY", "")
OTP_PROVIDER_CONFIGURED = bool(OTP_PROVIDER_API_KEY)

# SMTP / Email
if ENVIRONMENT == "live":
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
        raise ImproperlyConfigured(
            "Live environment requires SMTP configuration: set EMAIL_HOST, EMAIL_HOST_USER and EMAIL_HOST_PASSWORD."
        )
    EMAIL_CONFIGURED = True
else:
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_CONFIGURED = bool(EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)

# ============================================================
# Live-only integration checks
# - Ensure critical third-party secrets are present in live and fail fast otherwise
# ============================================================
if ENVIRONMENT == "live":
    # OTP (MSG91) required in live
    MSG91_AUTH_KEY = os.environ.get("MSG91_AUTH_KEY", "")
    MSG91_SENDER_ID = os.environ.get("MSG91_SENDER_ID", "")
    MSG91_TEMPLATE_ID = os.environ.get("MSG91_TEMPLATE_ID", "")
    if not (MSG91_AUTH_KEY and MSG91_SENDER_ID and MSG91_TEMPLATE_ID):
        raise ImproperlyConfigured(
            "Live environment requires MSG91_AUTH_KEY, MSG91_SENDER_ID and MSG91_TEMPLATE_ID to be set."
        )

    # Google OAuth required in live
    GCID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GCSC = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    if not (GCID and GCSC):
        raise ImproperlyConfigured(
            "Live environment requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to be set."
        )
>>>>>>> Stashed changes

# Analytics / pixels
GOOGLE_ANALYTICS_ID = os.environ.get("GOOGLE_ANALYTICS_ID", "")
META_PIXEL_ID = os.environ.get("META_PIXEL_ID", "")

<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes

# ============================================================
# DEFAULTS
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Contact configuration (single point of truth for contact email)
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "contact@domain.com")
