Verification TODOs
==================

1) Start Django in ENVIRONMENT=test
-----------------------------------

- Activate your Python virtualenv (required by project policy).

```bash
source venv/bin/activate
export ENVIRONMENT=test
# apply migrations (non-interactive)
python manage.py migrate --noinput
# start development server
python manage.py runserver
```

- Expected outcome: Django starts using SQLite, no real credentials required; static files served by the development server without running `collectstatic`.

2) Run payments E2E test file (if present)
-----------------------------------------

- File path: `payments_e2e_test.py` (project root).
- Run it from the Django environment (do not run arbitrarily outside the project). Example invocation while `ENVIRONMENT=test` and venv active:

```bash
source venv/bin/activate
export ENVIRONMENT=test
python manage.py shell < payments_e2e_test.py
```

- Expected outcome: The script calls `/payments/create-order/`, parses the returned JSON, simulates a Razorpay verification using the `RAZORPAY_KEY_SECRET` from the environment (or placeholder in test), posts to `/payments/verify/`, and prints DB state before/after. In test mode this should complete using placeholders or test keys without real credentials.

3) Verify live strictness (expected failure when creds missing)
-----------------------------------------------------------

- Steps (do not run unless you intend to confirm failure):

```bash
source venv/bin/activate
export ENVIRONMENT=live
# Ensure live-required secrets are NOT set (or unset them)
# e.g. unset SECRET_KEY DATABASE_URL RAZORPAY_KEY_ID RAZORPAY_KEY_SECRET EMAIL_HOST EMAIL_HOST_USER EMAIL_HOST_PASSWORD
python manage.py runserver
```

- Expected outcome: Django should fail early during settings import with an `ImproperlyConfigured` error indicating missing `SECRET_KEY` and/or required live credentials (Postgres/Razorpay/SMTP). This verifies live fails hard when credentials are absent.

Notes
-----
- Do not run these commands on a production host unless you know the effects. These are verification steps for local/test environments.
- The `payments_e2e_test.py` script is a project helper; it expects Django models and settings to be importable (run via `manage.py shell` as shown).
