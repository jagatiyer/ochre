from django.contrib import admin
from django.urls import path, include
from home import views as home_views

urlpatterns = [
    path("", home_views.index, name="home"),

    path("blog/", include("blog.urls", namespace="blog")),
    path("media/", include("mediahub.urls", namespace="mediahub")),
    path("commercials/", include("commercials.urls")),
    path("collections/", include("collections_app.urls")),

    path("shop/", include("shop.urls", namespace="shop")),

    path("contact/", include("contact.urls")),

    path("story/", include("story.urls")),

    path("accounts/", include("allauth.urls")),  # allauth
    path("admin/", admin.site.urls),

    # ---- YOUR NEW PROFILE ROUTE ----
    path("profile/", include("users.urls", namespace="users")),   # <-- note 'users' namespace

]
