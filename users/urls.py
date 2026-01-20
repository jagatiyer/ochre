# users/urls.py
from django.urls import path
from . import views

app_name = "users"   # <--- must match the namespace you use in include() and templates

urlpatterns = [
    path("", views.profile_view, name="profile"),         # /profile/
    path("edit/", views.profile_edit, name="profile_edit"),
    path("login/", views.login_options, name="login_options"),
    path("otp/start/", views.otp_start, name="otp_start"),
    path("otp/verify/", views.otp_verify, name="otp_verify"),
]
