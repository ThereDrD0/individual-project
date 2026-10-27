"""Скрипт импорта данных из JSON-файлов в базу данных SQLite."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from db.database import DB_PATH, get_connection, init_db

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

USERS_JSON = DATA_DIR / "users.json"
ITEMS_JSON = DATA_DIR / "items.json"
REQUESTS_JSON = DATA_DIR / "requests.json"
TRANSFERS_JSON = DATA_DIR / "transfers.json"


def _read_json_file(file_path: Path) -> list[dict]:
    """Считывает список объектов из указанного JSON-файла."""
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        return []


def import_data(db_path: Path | str = DB_PATH) -> None:
    """Выполняет иерархический импорт данных из JSON в SQLite."""
    init_db(db_path=db_path)

    users_data = _read_json_file(USERS_JSON)
    items_data = _read_json_file(ITEMS_JSON)
    requests_data = _read_json_file(REQUESTS_JSON)
    transfers_data = _read_json_file(TRANSFERS_JSON)

    conn = get_connection(db_path)
    try:
        users_rows = [
            (u["id"], u["name"], u.get("age"), u["sex"])
            for u in users_data
        ]
        conn.executemany(
            """
            INSERT INTO users (id, name, age, sex)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                age = excluded.age,
                sex = excluded.sex;
            """,
            users_rows,
        )

        items_rows = [
            (i["id"], i["name"], i.get("description"), i.get("owner_id"))
            for i in items_data
        ]
        conn.executemany(
            """
            INSERT INTO items (id, name, description, owner_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                owner_id = excluded.owner_id;
            """,
            items_rows,
        )

        requests_rows = [
            (
                r["id"],
                r["item_id"],
                r["old_user_id"],
                r["new_user_id"],
                r.get("status", "PENDING"),
                r["created_at"],
            )
            for r in requests_data
        ]
        conn.executemany(
            """
            INSERT INTO requests (
                id, item_id, old_user_id, new_user_id, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                item_id = excluded.item_id,
                old_user_id = excluded.old_user_id,
                new_user_id = excluded.new_user_id,
                status = excluded.status,
                created_at = excluded.created_at;
            """,
            requests_rows,
        )

        transfers_rows = [
            (
                t["id"],
                t["item_id"],
                t["from_user_id"],
                t["to_user_id"],
                t["transferred_at"],
            )
            for t in transfers_data
        ]
        conn.executemany(
            """
            INSERT INTO transfers (
                id, item_id, from_user_id, to_user_id, transferred_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                item_id = excluded.item_id,
                from_user_id = excluded.from_user_id,
                to_user_id = excluded.to_user_id,
                transferred_at = excluded.transferred_at;
            """,
            transfers_rows,
        )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    """Точка входа скрипта импорта."""
    try:
        import_data()
        print("Данные успешно импортированы в SQLite базу данных.")
    except Exception as exc:
        print(f"Ошибка при импорте данных: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
