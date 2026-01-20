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
    return {
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "")
    }

def global_feature_flags(request):
    return feature_flags(request)

