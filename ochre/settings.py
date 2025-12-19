from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

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

    # CKEditor 5 (rich text for blog admin)
    "django_ckeditor_5",

    # Project apps
    "home",
    "blog",
    "mediahub",
    "collections_app",
    "shop.apps.ShopConfig",
    "contact",
    "story",
    "users",
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
            ],
        },
    }
]


# ============================================================
# DATABASE
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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


# ============================================================
# MEDIA FILES  ✅ CRITICAL FOR BLOG IMAGES
# ============================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# TinyMCE Cloud API key - read from environment. Set this in production.
import os
TINYMCE_API_KEY = os.environ.get('TINYMCE_API_KEY')

# CKEditor5 upload path (relative to MEDIA_ROOT)
CKEDITOR5_UPLOAD_PATH = "ckeditor5/"

# CKEditor5 configuration: use Base64 image embedding only and toolbar
CKEDITOR5_CONFIGS = {
    "default": {
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
        # No simpleUpload / uploadUrl configured — editor will use base64
        # embedding (Base64UploadAdapter) if available in the build.
        # This keeps all image embedding client-side only.
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


# ============================================================
# DEFAULTS
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
