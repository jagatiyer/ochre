from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DummyOTPProvider:
    """Development-friendly OTP provider.

    - `send_otp(phone)` returns a request_id string (for tracking)
    - `verify_otp(phone, code, request_id)` returns True if code matches '123456'
    """

    def send_otp(self, phone):
        # In real providers you'd call their API. Here we log and return a dummy id.
        logger.info('DummyOTPProvider send_otp to %s', phone)
        return 'dummy-request'

    def verify_otp(self, phone, code, request_id=None):
        logger.info('DummyOTPProvider verify_otp %s %s', phone, code)
        return code.strip() in ('123456', '000000')


def get_provider():
    """Return an OTP provider instance based on settings. Falling back to DummyOTPProvider."""
    backend = getattr(settings, 'OTP_PROVIDER_BACKEND', '')
    if backend:
        try:
            module_path, cls_name = backend.rsplit('.', 1)
            module = __import__(module_path, fromlist=[cls_name])
            cls = getattr(module, cls_name)
            return cls()
        except Exception:
            logger.exception('Failed to load OTP_PROVIDER_BACKEND %s', backend)
    return DummyOTPProvider()
