"""View-функции для приложения items."""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

import storage


def item_list(request: HttpRequest) -> HttpResponse:
    """Отображает каталог вещей с возможностью фильтрации по статусу."""
    users, items, requests, transfers = storage.load_all_data()

    status_filter = request.GET.get("status", "all")
    if status_filter == "free":
        filtered_items = [it for it in items if it.owner is None]
    elif status_filter == "busy":
        filtered_items = [it for it in items if it.owner is not None]
    else:
        filtered_items = items
        status_filter = "all"

    context = {
        "title": "Каталог вещей — Площадка совместного использования",
        "items": filtered_items,
        "current_filter": status_filter,
        "total_count": len(items),
    }
    return render(request, "items/item_list.html", context)


def item_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    """Отображает детальную карточку вещи и её историю."""
    users, items, requests, transfers = storage.load_all_data()

    item = next((it for it in items if it.id == item_id), None)
    if item is None:
        raise Http404(f"Вещь с идентификатором {item_id} не найдена.")

    item_transfers = [t for t in transfers if t.item_id == item_id]
    item_requests = [r for r in requests if r.item.id == item_id]

    context = {
        "title": f"{item.name} — Детали вещи",
        "item": item,
        "transfers": item_transfers,
        "requests": item_requests,
    }
    return render(request, "items/item_detail.html", context)
