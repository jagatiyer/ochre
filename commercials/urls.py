from django.urls import path
from django.http import HttpResponse

urlpatterns = [
    path("", lambda request: HttpResponse("Commercials index placeholder"), name="commercials_index"),
]
