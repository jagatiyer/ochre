# ochre/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from home import views as home_views
from story import views as story_views
from pages import views as pages_views
from shop import views as shop_views   # ✅ correct import


urlpatterns = [
    path("", home_views.index, name="home"),

    # Core site sections
    path("collections/", include("collections_app.urls", namespace="collections_app")),
    path("commercials/", include("commercials.urls")),
    path("mediahub/", include("mediahub.urls")),
    path("story/", include("story.urls", namespace="story")),
    path("society/", story_views.society_page, name="society"),
    path("blog/", include("blog.urls", namespace="blog")),
    path("contact/", include("contact.urls", namespace="contact")),
    path("shop/", include("shop.urls", namespace="shop")),
    path("payments/", include("payments.urls", namespace="payments")),

    # Static pages
    path("pages/<slug:slug>/", pages_views.staticpage_detail, name="static_page"),

    # CKEditor5
    path("ckeditor5/", include("django_ckeditor_5.urls")),

    # Auth / users
    path("profile/", include("users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    
    # ✅ Orders route (ONLY ONCE)
    path("account/orders/", shop_views.my_orders, name="my_orders"),

    # Admin
    path("admin/", admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )