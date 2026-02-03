from django.shortcuts import render, get_object_or_404
from .models import CollectionItem, CollectionCategory
from django.db import models

# -----------------------------------------------------------------------------
# COLLECTIONS LIST PAGE (matches BLOG list layout + filter UI)
# -----------------------------------------------------------------------------

def collections_index(request):
    category = request.GET.get("category", "all")

    # Categories are now admin-managed. Show only active categories ordered
    # by the admin-defined `order` field.
    categories = CollectionCategory.objects.filter(is_active=True).order_by("order")

    # Filtering logic: prefer the FK relation when present, otherwise fall
    # back to the legacy string `category` for older rows.
    if category == "all":
        items = CollectionItem.objects.filter(published=True).order_by("-created_at")
    else:
        # Only fall back to the legacy string `category` when the FK is
        # not populated. This prevents the default value on the legacy
        # `category` field from matching all rows unintentionally.
        items = (
            CollectionItem.objects.filter(published=True)
            .filter(
                models.Q(category_fk__slug=category)
                | (models.Q(category_fk__isnull=True) & models.Q(category__iexact=category))
            )
            .order_by("-created_at")
        )

    context = {
        "items": items,
        "active_category": category,
        "categories": categories,
    }

    return render(request, "collections/collections_list.html", context)



# -----------------------------------------------------------------------------
# COLLECTION ITEM DETAIL PAGE
# -----------------------------------------------------------------------------

def collectionitem_detail(request, pk):
    item = get_object_or_404(CollectionItem, pk=pk)
    return render(request, "collections/collectionitem_detail.html", {"item": item})




def collections_by_category(request, category):
    items = (
        CollectionItem.objects.filter(published=True)
        .filter(
            models.Q(category_fk__slug=category)
            | (models.Q(category_fk__isnull=True) & models.Q(category__iexact=category))
        )
        .order_by("-created_at")
    )

    categories = CollectionCategory.objects.filter(is_active=True).order_by("order")

    context = {
        "items": items,
        "active_category": category,
        "categories": categories,
    }
    return render(request, "collections/collections_list.html", context)
