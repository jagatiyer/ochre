from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("<slug:slug>/", views.staticpage_detail, name="detail"),
]
