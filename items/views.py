"""View-функции для приложения items на базе SQLite."""

from __future__ import annotations

from types import SimpleNamespace

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from models.item_request import ItemRequestStatus
from models.user import Sex


def item_list(request: HttpRequest) -> HttpResponse:
    """Отображает каталог вещей с возможностью фильтрации по статусу."""
    status_filter = request.GET.get("status", "all")
    conn = get_connection()
    try:
        total_count = conn.execute(
            "SELECT COUNT(*) FROM items;"
        ).fetchone()[0]

        base_query = """
            SELECT
                items.id,
                items.name,
                items.description,
                items.owner_id,
                users.name AS owner_name
            FROM items
            LEFT JOIN users ON items.owner_id = users.id
        """

        if status_filter == "free":
            query = (
                f"{base_query} WHERE items.owner_id IS NULL "
                "ORDER BY items.id ASC;"
            )
            rows = conn.execute(query).fetchall()
        elif status_filter == "busy":
            query = (
                f"{base_query} WHERE items.owner_id IS NOT NULL "
                "ORDER BY items.id ASC;"
            )
            rows = conn.execute(query).fetchall()
        else:
            status_filter = "all"
            query = f"{base_query} ORDER BY items.id ASC;"
            rows = conn.execute(query).fetchall()

        items = [
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
            for row in rows
        ]
    finally:
        conn.close()

    context = {
        "title": "Каталог вещей — Площадка совместного использования",
        "items": items,
        "current_filter": status_filter,
        "total_count": total_count,
    }
    return render(request, "items/item_list.html", context)


def item_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    """Отображает детальную карточку вещи и её историю."""
    conn = get_connection()
    try:
        item_row = conn.execute(
            """
            SELECT
                items.id,
                items.name,
                items.description,
                items.owner_id,
                users.name AS owner_name,
                users.age AS owner_age,
                users.sex AS owner_sex
            FROM items
            LEFT JOIN users ON items.owner_id = users.id
            WHERE items.id = ?;
            """,
            (item_id,),
        ).fetchone()

        if item_row is None:
            raise Http404(f"Вещь с идентификатором {item_id} не найдена.")

        owner = None
        if item_row["owner_id"] is not None:
            sex = (
                Sex(item_row["owner_sex"])
                if item_row["owner_sex"] is not None
                else None
            )
            owner = SimpleNamespace(
                id=item_row["owner_id"],
                name=item_row["owner_name"],
                age=item_row["owner_age"],
                sex=sex,
            )

        item = SimpleNamespace(
            id=item_row["id"],
            name=item_row["name"],
            description=item_row["description"],
            owner=owner,
        )

        transfer_rows = conn.execute(
            """
            SELECT
                t.id,
                t.item_id,
                t.from_user_id,
                t.to_user_id,
                t.transferred_at,
                from_u.name AS from_user_name,
                to_u.name AS to_user_name
            FROM transfers AS t
            JOIN users AS from_u ON t.from_user_id = from_u.id
            JOIN users AS to_u ON t.to_user_id = to_u.id
            WHERE t.item_id = ?
            ORDER BY t.transferred_at DESC, t.id DESC;
            """,
            (item_id,),
        ).fetchall()

        transfers = [
            SimpleNamespace(
                id=t["id"],
                item_id=t["item_id"],
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

        request_rows = conn.execute(
            """
            SELECT
                r.id,
                r.item_id,
                r.old_user_id,
                r.new_user_id,
                r.status,
                r.created_at,
                new_u.name AS new_user_name,
                old_u.name AS old_user_name
            FROM requests AS r
            JOIN users AS new_u ON r.new_user_id = new_u.id
            JOIN users AS old_u ON r.old_user_id = old_u.id
            WHERE r.item_id = ?
            ORDER BY r.created_at DESC, r.id DESC;
            """,
            (item_id,),
        ).fetchall()

        requests = [
            SimpleNamespace(
                id=r["id"],
                item_id=r["item_id"],
                new_user=SimpleNamespace(
                    id=r["new_user_id"],
                    name=r["new_user_name"],
                ),
                old_user=SimpleNamespace(
                    id=r["old_user_id"],
                    name=r["old_user_name"],
                ),
                status=ItemRequestStatus[r["status"]],
                created_at=r["created_at"],
            )
            for r in request_rows
        ]
    finally:
        conn.close()

    context = {
        "title": f"{item.name} — Детали вещи",
        "item": item,
        "transfers": transfers,
        "requests": requests,
    }
    return render(request, "items/item_detail.html", context)


def available_items(request: HttpRequest) -> HttpResponse:
    """Отображает список свободных вещей с возможностью поиска."""
    q = request.GET.get("q", "").strip()
    conn = get_connection()
    try:
        if q:
            rows = conn.execute(
                """
                SELECT items.id, items.name, items.description
                FROM items
                WHERE items.owner_id IS NULL AND items.name LIKE ?
                ORDER BY items.name;
                """,
                (f"%{q}%",),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT items.id, items.name, items.description
                FROM items
                WHERE items.owner_id IS NULL
                ORDER BY items.name;
                """
            ).fetchall()

        items = [
            SimpleNamespace(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                owner=None,
            )
            for row in rows
        ]
    finally:
        conn.close()

    context = {
        "items": items,
        "query": q,
        "title": "Поиск свободных вещей",
    }
    return render(request, "items/available.html", context)
