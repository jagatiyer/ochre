from django.conf import settings

def feature_flags(request):
    return {
        "GOOGLE_OAUTH_AVAILABLE": bool(
            getattr(settings, "GOOGLE_CLIENT_ID", "")
        ),
        "RAZORPAY_AVAILABLE": bool(
            getattr(settings, "RAZORPAY_KEY_ID", "")
        ),
        "EMAIL_ENABLED": bool(
            getattr(settings, "EMAIL_HOST_USER", "")
        ),
        "SMS_OTP_AVAILABLE": bool(
            getattr(settings, "MSG91_AUTH_KEY", "")
        ),
    }

def contact_email(request):
<<<<<<< Updated upstream
    return {
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "")
    }

def global_feature_flags(request):
    return feature_flags(request)

=======
    """Expose CONTACT_EMAIL to templates as `CONTACT_EMAIL`."""
    return {"CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "contact@domain.com")}


def global_feature_flags(request):
    """Expose integration readiness flags to templates.

    Provides keys:
      - RAZORPAY_TEST_KEYS_PROVIDED
      - GOOGLE_OAUTH_CONFIGURED
      - OTP_PROVIDER_CONFIGURED
      - EMAIL_CONFIGURED
      - GOOGLE_ANALYTICS_ID
      - META_PIXEL_ID
    """
    return {
        "RAZORPAY_TEST_KEYS_PROVIDED": getattr(settings, "RAZORPAY_TEST_KEYS_PROVIDED", False),
        "GOOGLE_OAUTH_CONFIGURED": getattr(settings, "GOOGLE_OAUTH_CONFIGURED", False),
        "OTP_PROVIDER_CONFIGURED": getattr(settings, "OTP_PROVIDER_CONFIGURED", False),
        "EMAIL_CONFIGURED": getattr(settings, "EMAIL_CONFIGURED", False),
        "GOOGLE_ANALYTICS_ID": getattr(settings, "GOOGLE_ANALYTICS_ID", ""),
        "META_PIXEL_ID": getattr(settings, "META_PIXEL_ID", ""),
    }
>>>>>>> Stashed changes
