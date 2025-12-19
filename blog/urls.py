from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.blog_list, name="blog_list"),
    path("load-more/", views.blog_list_more, name="blog_list_more"),
    path("tinymce/upload/", views.tinymce_upload, name="tinymce_upload"),
    path("<slug:slug>/", views.blog_detail, name="blog_detail"),
]
