# profile/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import ProfileForm

from django.conf import settings
from django.shortcuts import reverse
from django.contrib.auth import login
from django.contrib.auth.models import User
from .otp_provider import get_provider


def otp_start(request):
    """Start OTP flow: enter mobile number, send OTP via provider."""
    provider = get_provider()
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if not phone:
            return render(request, 'users/otp_start.html', {'error': 'Enter mobile number'})
        req_id = provider.send_otp(phone)
        # store minimal session state
        request.session['otp_phone'] = phone
        request.session['otp_request_id'] = req_id
        request.session['otp_sent'] = True
        return redirect('users:otp_verify')
    return render(request, 'users/otp_start.html', {})


def otp_verify(request):
    provider = get_provider()
    phone = request.session.get('otp_phone')
    req_id = request.session.get('otp_request_id')
    if request.method == 'POST':
        code = request.POST.get('code')
        if provider.verify_otp(phone, code, req_id):
            # Create or get user associated with phone (username=phone)
            user, created = User.objects.get_or_create(username=phone, defaults={'email': ''})
            # Log the user in
            login(request, user)
            # Clean session OTP state
            for k in ('otp_phone', 'otp_request_id', 'otp_sent'):
                request.session.pop(k, None)
            return redirect('/')
        return render(request, 'users/otp_verify.html', {'error': 'Invalid code'})
    return render(request, 'users/otp_verify.html', {'phone': phone})


def login_options(request):
    """Show login options (Google, OTP) and graceful messaging when unavailable."""
    return render(request, "users/login_options.html", {})

@login_required
def profile_view(request):
    """
    Simple profile page that displays user info and links to edit.
    """
    user = request.user
    context = {"user": user}
    return render(request, "users/profile.html", context)


@login_required
def profile_edit(request):
    """
    Edit basic user details (first_name, last_name, email).
    Uses ProfileForm in profile/forms.py.
    """
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile:profile")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileForm(instance=user)

    return render(request, "users/profile_edit.html", {"form": form})
