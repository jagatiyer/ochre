# Environment Contract & Feature Flags

This file documents the environment variables the project recognizes and the expected behavior when they are present or absent.

1) Razorpay (payments)
  - `RAZORPAY_KEY_ID` (required for live/test API calls)
  - `RAZORPAY_KEY_SECRET` (required)
  - Behavior: If both are present the site will use them for creating orders and signature verification. If absent, the site boots in demo mode using harmless placeholders and no secrets are required.

2) Google OAuth (social login)
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - Behavior: When both are set, Google OAuth UI buttons become active and `allauth` can be configured. Otherwise the login UI shows a graceful "temporarily unavailable" message.

  - Implementation notes:
    - The project reads `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from the environment and exposes a template flag `GOOGLE_OAUTH_CONFIGURED` so the login UI can hide/show the Google button.
    - Allauth routes are already wired at `/accounts/` and the Google provider is enabled via `allauth.socialaccount.providers.google` in `INSTALLED_APPS`.
    - To enable Google OAuth in production: create OAuth credentials in Google Cloud Console, set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` as environment variables, then restart Django.


3) OTP provider (phone verification)
  - `OTP_PROVIDER_API_KEY` (generic key for whatever provider you integrate)
  - Behavior: If present, OTP login UI is enabled. Otherwise the option is disabled.

  - Implementation notes (developer-friendly):
    - The code supports a pluggable backend via `OTP_PROVIDER_BACKEND` (a dotted Python path to a class). If unset, a `DummyOTPProvider` is used for local development which accepts test codes `123456` or `000000`.
    - The template flag `OTP_PROVIDER_CONFIGURED` is computed from `OTP_PROVIDER_BACKEND` or the presence of `OTP_PROVIDER_API_KEY` so UI can hide the OTP option when not configured.
    - The OTP flow uses the Django session to keep minimal state (`otp_phone`, `otp_request_id`, `otp_sent`) and does NOT persist OTPs in the database.
    - To enable a real provider, implement a small backend class with `send_otp(phone)` and `verify_otp(phone, code, request_id=None)` and set `OTP_PROVIDER_BACKEND=path.to.YourProvider` in the environment.


4) Email / SMTP
  - `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
  - Behavior: If all three are present, email sending is considered configured (for account emails, password reset). Otherwise email features are disabled.

5) Analytics / Pixels
  - `GOOGLE_ANALYTICS_ID` (e.g., `G-XXXXXXXX`)
  - `META_PIXEL_ID` (Facebook / Meta Pixel ID)
  - Behavior: When present, templates will include the corresponding snippets.

Notes:
  - No secrets are stored in the repo. Real credentials must be provided via environment variables or a secure secrets manager.
  - Adding environment variables in your shell and restarting the Django server is sufficient to "light up" features.

System readiness / admin checks (quick):

- Google OAuth: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` must be set. The template flag `GOOGLE_OAUTH_CONFIGURED` will be True when configured.
- OTP provider: set `OTP_PROVIDER_BACKEND` to a valid class path or `OTP_PROVIDER_API_KEY` for your vendor. The template flag `OTP_PROVIDER_CONFIGURED` will be True when configured.
- Email: ensure `EMAIL_HOST`, `EMAIL_HOST_USER`, and `EMAIL_HOST_PASSWORD` are set; `EMAIL_CONFIGURED` will be True when provided.

Example local dev (bash / zsh):

```bash
export GOOGLE_CLIENT_ID=your-google-client-id
export GOOGLE_CLIENT_SECRET=your-google-client-secret
# Optional: OTP provider
export OTP_PROVIDER_BACKEND=myproj.otp_backends.MyProvider
# Or set OTP_PROVIDER_API_KEY if your wrapper uses a single key
export OTP_PROVIDER_API_KEY=your-otp-key

# Email (optional)
export EMAIL_HOST=smtp.example.com
export EMAIL_HOST_USER=you@example.com
export EMAIL_HOST_PASSWORD=secret
```

Example local dev (bash / zsh):

```bash
export RAZORPAY_KEY_ID=rzp_test_xxx
export RAZORPAY_KEY_SECRET=rzp_test_secret
export GOOGLE_CLIENT_ID=...
export GOOGLE_CLIENT_SECRET=...
export OTP_PROVIDER_API_KEY=...
export EMAIL_HOST=smtp.example.com
export EMAIL_HOST_USER=you@example.com
export EMAIL_HOST_PASSWORD=secret
export GOOGLE_ANALYTICS_ID=G-XXXXXXXX
export META_PIXEL_ID=1234567890
```
