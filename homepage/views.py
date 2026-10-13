"""View-функции для приложения homepage."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.item_request import ItemRequestStatus
import storage


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница сервиса совместного использования."""
    users, items, requests, transfers = storage.load_all_data()

    total_items = len(items)
    free_items = len([it for it in items if it.owner is None])
    busy_items = len([it for it in items if it.owner is not None])
    total_requests = len(requests)
    pending_requests = len(
        [r for r in requests if r.status == ItemRequestStatus.PENDING]
    )
    total_transfers = len(transfers)

    context = {
        "title": "Главная — Площадка совместного использования",
        "stats": {
            "total_items": total_items,
            "free_items": free_items,
            "busy_items": busy_items,
            "total_requests": total_requests,
            "pending_requests": pending_requests,
            "total_transfers": total_transfers,
            "total_users": len(users),
        },
        "recent_items": items[:4],
        "recent_transfers": transfers[:3],
    }
    return render(request, "homepage/index.html", context)


def custom_page_not_found(
    request: HttpRequest,
    exception: Exception | None = None,
) -> HttpResponse:
    """Обработчик ошибки 404 (Страница не найдена)."""
    context = {
        "title": "404 — Страница не найдена",
        "path": request.path,
    }
    return render(request, "404.html", context, status=404)
