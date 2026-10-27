"""View-функции для приложения item_requests на базе SQLite."""

from __future__ import annotations

from types import SimpleNamespace

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from models.item_request import ItemRequestStatus


def request_list(request: HttpRequest) -> HttpResponse:
    """Отображает список всех запросов на предметы и историю передач."""
    conn = get_connection()
    try:
        request_rows = conn.execute(
            """
            SELECT
                r.id,
                r.item_id,
                r.old_user_id,
                r.new_user_id,
                r.status,
                r.created_at,
                i.name AS item_name,
                old_u.name AS old_user_name,
                new_u.name AS new_user_name
            FROM requests AS r
            JOIN items AS i ON r.item_id = i.id
            JOIN users AS old_u ON r.old_user_id = old_u.id
            JOIN users AS new_u ON r.new_user_id = new_u.id
            ORDER BY r.created_at DESC, r.id DESC;
            """
        ).fetchall()

        requests = [
            SimpleNamespace(
                id=row["id"],
                item=SimpleNamespace(
                    id=row["item_id"],
                    name=row["item_name"],
                ),
                old_user=SimpleNamespace(
                    id=row["old_user_id"],
                    name=row["old_user_name"],
                ),
                new_user=SimpleNamespace(
                    id=row["new_user_id"],
                    name=row["new_user_name"],
                ),
                status=ItemRequestStatus[row["status"]],
                created_at=row["created_at"],
            )
            for row in request_rows
        ]

        transfer_rows = conn.execute(
            """
            SELECT
                t.id,
                t.item_id,
                t.from_user_id,
                t.to_user_id,
                t.transferred_at,
                i.name AS item_name,
                from_u.name AS from_user_name,
                to_u.name AS to_user_name
            FROM transfers AS t
            JOIN items AS i ON t.item_id = i.id
            JOIN users AS from_u ON t.from_user_id = from_u.id
            JOIN users AS to_u ON t.to_user_id = to_u.id
            ORDER BY t.transferred_at DESC, t.id DESC;
            """
        ).fetchall()

        transfers = [
            SimpleNamespace(
                id=t["id"],
                item_id=t["item_id"],
                item=SimpleNamespace(
                    id=t["item_id"],
                    name=t["item_name"],
                ),
                from_user=SimpleNamespace(
                    id=t["from_user_id"],
                    name=t["from_user_name"],
                ),
                to_user=SimpleNamespace(
                    id=t["to_user_id"],
                    name=t["to_user_name"],
                ),
                transferred_at=t["transferred_at"],
            )
            for t in transfer_rows
        ]
    finally:
        conn.close()

    context = {
        "title": "Запросы и передачи — Площадка совместного использования",
        "requests": requests,
        "transfers": transfers,
    }
    return render(request, "item_requests/request_list.html", context)


def request_detail(request: HttpRequest, request_id: int) -> HttpResponse:
    """Отображает детальную информацию по конкретному запросу."""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT
                r.id,
                r.item_id,
                r.old_user_id,
                r.new_user_id,
                r.status,
                r.created_at,
                i.name AS item_name,
                old_u.name AS old_user_name,
                new_u.name AS new_user_name
            FROM requests AS r
            JOIN items AS i ON r.item_id = i.id
            JOIN users AS old_u ON r.old_user_id = old_u.id
            JOIN users AS new_u ON r.new_user_id = new_u.id
            WHERE r.id = ?;
            """,
            (request_id,),
        ).fetchone()

        if row is None:
            raise Http404(
                f"Запрос с идентификатором {request_id} не найден."
            )

        req = SimpleNamespace(
            id=row["id"],
            item=SimpleNamespace(
                id=row["item_id"],
                name=row["item_name"],
            ),
            old_user=SimpleNamespace(
                id=row["old_user_id"],
                name=row["old_user_name"],
            ),
            new_user=SimpleNamespace(
                id=row["new_user_id"],
                name=row["new_user_name"],
            ),
            status=ItemRequestStatus[row["status"]],
            created_at=row["created_at"],
        )
    finally:
        conn.close()

    context = {
        "title": f"Запрос #{req.id} — {req.item.name}",
        "req": req,
    }
    return render(request, "item_requests/request_detail.html", context)


def statistics(request: HttpRequest) -> HttpResponse:
    """Отображает аналитическую статистику популярности вещей."""
    conn = get_connection()
    try:
        popular_rows = conn.execute(
            """
            SELECT items.id, items.name, COUNT(requests.id) AS requests_count
            FROM items
            LEFT JOIN requests ON items.id = requests.item_id
            GROUP BY items.id, items.name
            ORDER BY requests_count DESC, items.name ASC;
            """
        ).fetchall()

        popular_items = [
            SimpleNamespace(
                id=row["id"],
                name=row["name"],
                requests_count=row["requests_count"],
            )
            for row in popular_rows
        ]

        active_rows = conn.execute(
            """
            SELECT items.id, items.name, COUNT(requests.id) AS requests_count
            FROM items
            JOIN requests ON items.id = requests.item_id
            GROUP BY items.id, items.name
            HAVING COUNT(requests.id) >= 1
            ORDER BY requests_count DESC;
            """
        ).fetchall()

        items_with_requests = [
            SimpleNamespace(
                id=row["id"],
                name=row["name"],
                requests_count=row["requests_count"],
            )
            for row in active_rows
        ]
    finally:
        conn.close()

    context = {
        "popular_items": popular_items,
        "items_with_requests": items_with_requests,
        "title": "Статистика сервиса",
    }
    return render(request, "item_requests/statistics.html", context)
