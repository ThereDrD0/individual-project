"""View-функции для приложения homepage на базе SQLite."""

from __future__ import annotations

from types import SimpleNamespace

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница сервиса совместного использования."""
    conn = get_connection()
    try:
        items_stats = conn.execute(
            """
            SELECT
                COUNT(*) AS total_items,
                COUNT(CASE WHEN owner_id IS NULL THEN 1 END) AS free_items,
                COUNT(owner_id) AS busy_items
            FROM items;
            """
        ).fetchone()

        requests_stats = conn.execute(
            """
            SELECT
                COUNT(*) AS total_requests,
                COUNT(CASE WHEN status = 'PENDING' THEN 1 END)
                    AS pending_requests
            FROM requests;
            """
        ).fetchone()

        total_transfers = conn.execute(
            "SELECT COUNT(*) FROM transfers;"
        ).fetchone()[0]

        total_users = conn.execute(
            "SELECT COUNT(*) FROM users;"
        ).fetchone()[0]

        recent_items_rows = conn.execute(
            """
            SELECT
                items.id,
                items.name,
                items.description,
                items.owner_id,
                users.name AS owner_name
            FROM items
            LEFT JOIN users ON items.owner_id = users.id
            ORDER BY items.id ASC
            LIMIT 4;
            """
        ).fetchall()

        recent_items = [
            SimpleNamespace(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                owner=(
                    SimpleNamespace(
                        id=row["owner_id"],
                        name=row["owner_name"],
                    )
                    if row["owner_id"] is not None
                    else None
                ),
            )
            for row in recent_items_rows
        ]

        recent_transfers_rows = conn.execute(
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
            ORDER BY t.transferred_at DESC, t.id DESC
            LIMIT 3;
            """
        ).fetchall()

        recent_transfers = [
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
            for t in recent_transfers_rows
        ]
    finally:
        conn.close()

    context = {
        "title": "Главная — Площадка совместного использования",
        "stats": {
            "total_items": items_stats["total_items"],
            "free_items": items_stats["free_items"],
            "busy_items": items_stats["busy_items"],
            "total_requests": requests_stats["total_requests"],
            "pending_requests": requests_stats["pending_requests"],
            "total_transfers": total_transfers,
            "total_users": total_users,
        },
        "recent_items": recent_items,
        "recent_transfers": recent_transfers,
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
