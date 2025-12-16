from django.shortcuts import render, get_object_or_404
from .models import CollectionItem, CATEGORY_CHOICES

from .models import CollectionItem

# -----------------------------------------------------------------------------
# COLLECTIONS LIST PAGE (matches BLOG list layout + filter UI)
# -----------------------------------------------------------------------------

def collections_index(request):
    category = request.GET.get("category", "all")

    # Categories shown in the filter bar (same as blog filter style)
    categories = [
        ("gin", "Gin"),
        ("vodka", "Vodka"),
        ("whiskey", "Whiskey"),
        ("limited", "Limited Edition"),
    ]

    # Filtering logic
    if category == "all":
        items = CollectionItem.objects.filter(published=True).order_by("-created_at")
    else:
        items = CollectionItem.objects.filter(
            category=category,
            published=True
        ).order_by("-created_at")

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
    items = CollectionItem.objects.filter(category=category).order_by("-created_at")

    context = {
        "items": items,
        "active_category": category,
        "categories": CATEGORY_CHOICES,
    }
    return render(request, "collections/collections_list.html", context)
