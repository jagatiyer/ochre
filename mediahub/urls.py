from django.urls import path
from . import views

app_name = "mediahub"

urlpatterns = [
    path("", views.media_index, name="media_index"),
    path("press/<slug:slug>/", views.press_detail, name="press_detail"),
]
