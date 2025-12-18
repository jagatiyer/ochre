# ochre/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from home import views as home_views

# --------------------------------------------------
# URL PATTERNS (MUST BE DEFINED FIRST)
# --------------------------------------------------

urlpatterns = [
    path("", home_views.index, name="home"),

    # Core site sections
    path("collections/", include("collections_app.urls", namespace="collections_app")),
    path("commercials/", include("commercials.urls")),
    path("mediahub/", include("mediahub.urls")),
    path("story/", include("story.urls", namespace="story")),
    path("blog/", include("blog.urls", namespace="blog")),
    path("contact/", include("contact.urls", namespace="contact")),
    path("shop/", include("shop.urls", namespace="shop")),

    # Auth / users
    path("profile/", include("users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),

    # Admin
    path("admin/", admin.site.urls),
]

# --------------------------------------------------
# MEDIA FILES (ONLY APPEND AFTER urlpatterns EXISTS)
# --------------------------------------------------

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
