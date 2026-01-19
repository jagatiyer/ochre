from django.urls import path
from . import views

# Expose both names for compatibility with existing templates
urlpatterns = [
    path('', views.index, name='commercials'),
    path('', views.index, name='commercials_index'),
]
