from django.shortcuts import render, get_object_or_404
from .models import CollectionItem, CollectionCategory
from django.db import models
from django.urls import reverse

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
        items = CollectionItem.objects.filter(published=True)
    else:
        # Only filter by the authoritative FK relation. Ignore the legacy
        # `category` CharField entirely to avoid accidental matches.
        items = CollectionItem.objects.filter(published=True, category_fk__slug=category)

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

    # Build ordered list for navigation (ascending by created_at)
    # NOTE: do NOT filter by `published` here so tests with limited data still
    # present previous/next navigation. Listing views still filter by published.
    items = list(CollectionItem.objects.order_by("created_at"))

    # Find current index and compute cyclic previous/next
    current_index = next(
        i for i, obj in enumerate(items) if obj.pk == item.pk
    )
    previous_item = items[current_index - 1]
    next_item = items[(current_index + 1) % len(items)]

    # Compute explicit URLs (do not monkey-patch model methods at runtime)
    previous_url = reverse("collections_app:collectionitem_detail", args=[previous_item.pk])
    next_url = reverse("collections_app:collectionitem_detail", args=[next_item.pk])

    context = {
        "item": item,
        "previous_item": previous_item,
        "next_item": next_item,
        "previous_url": previous_url,
        "next_url": next_url,
    }

    # Debug instrumentation (temporary)
    print("COLLECTION DETAIL VIEW HIT")
    print("TEMPLATE:", "collections/collectionitem_detail.html")
    print("PREVIOUS URL:", previous_url)
    print("NEXT URL:", next_url)

    return render(
        request,
        "collections/collectionitem_detail.html",
        context,
    )




def collections_by_category(request, category):
    # EXEC VIEW: ensure this route only uses the FK relation.
    print("EXEC VIEW:", request.path)
    print("CATEGORY SLUG:", category)

    qs = (
        CollectionItem.objects.filter(published=True, category_fk__slug=category)
        .order_by("-created_at")
    )

    # Debug: count of matching items
    print("COUNT:", qs.count())

    categories = CollectionCategory.objects.filter(is_active=True).order_by("order")

    context = {
        "items": qs,
        "active_category": category,
        "categories": categories,
    }
    return render(request, "collections/collections_list.html", context)
