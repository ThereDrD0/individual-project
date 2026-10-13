"""View-функции для приложения item_requests."""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

import storage


def request_list(request: HttpRequest) -> HttpResponse:
    """Отображает список всех запросов на предметы и историю передач."""
    users, items, requests, transfers = storage.load_all_data()

    context = {
        "title": "Запросы и передачи — Площадка совместного использования",
        "requests": requests,
        "transfers": transfers,
    }
    return render(request, "item_requests/request_list.html", context)


def request_detail(request: HttpRequest, request_id: int) -> HttpResponse:
    """Отображает детальную информацию по конкретному запросу."""
    users, items, requests, transfers = storage.load_all_data()

    req = next((r for r in requests if r.id == request_id), None)
    if req is None:
        raise Http404(f"Запрос с идентификатором {request_id} не найден.")

    context = {
        "title": f"Запрос #{req.id} — {req.item.name}",
        "req": req,
    }
    return render(request, "item_requests/request_detail.html", context)
