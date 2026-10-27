"""Тесты для слоя базы данных SQLite."""

from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from db.database import BASE_DIR, get_connection, init_db
from db.import_json import import_data


def test_init_db(tmp_path: Path) -> None:
    """Проверяет создание таблиц при инициализации базы данных."""
    db_file = tmp_path / "test.sqlite"
    init_db(db_path=db_file)

    conn = get_connection(db_file)
    try:
        tables = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
            """
        ).fetchall()
        table_names = [row["name"] for row in tables]
        assert table_names == ["items", "requests", "transfers", "users"]
    finally:
        conn.close()


def test_connection_settings(tmp_path: Path) -> None:
    """Проверяет включение foreign_keys и row_factory."""
    db_file = tmp_path / "test.sqlite"
    conn = get_connection(db_file)
    try:
        fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk == 1
        assert conn.row_factory == sqlite3.Row
    finally:
        conn.close()


def test_import_data(tmp_path: Path) -> None:
    """Проверяет импорт JSON данных в тестовую базу данных."""
    db_file = tmp_path / "test_import.sqlite"
    import_data(db_path=db_file)

    conn = get_connection(db_file)
    try:
        users_count = conn.execute("SELECT COUNT(*) FROM users;").fetchone()[0]
        items_count = conn.execute("SELECT COUNT(*) FROM items;").fetchone()[0]
        assert users_count > 0
        assert items_count > 0
    finally:
        conn.close()


def test_import_data_idempotent(tmp_path: Path) -> None:
    """Проверяет идемпотентность повторного импорта данных."""
    db_file = tmp_path / "test_reimport.sqlite"
    import_data(db_path=db_file)
    import_data(db_path=db_file)

    conn = get_connection(db_file)
    try:
        users = conn.execute("SELECT COUNT(*) FROM users;").fetchone()[0]
        items = conn.execute("SELECT COUNT(*) FROM items;").fetchone()[0]
        requests = conn.execute(
            "SELECT COUNT(*) FROM requests;"
        ).fetchone()[0]
        transfers = conn.execute(
            "SELECT COUNT(*) FROM transfers;"
        ).fetchone()[0]
        assert users == 8
        assert items == 12
        assert requests == 5
        assert transfers == 3
    finally:
        conn.close()


def test_foreign_key_integrity(tmp_path: Path) -> None:
    """Проверяет соблюдение целостности внешних ключей."""
    db_file = tmp_path / "test_fk.sqlite"
    init_db(db_path=db_file)

    conn = get_connection(db_file)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO items (id, name, owner_id) VALUES (?, ?, ?);",
                (1, "Тестовый предмет", 9999),
            )
    finally:
        conn.close()


def test_queries_execution(tmp_path: Path) -> None:
    """Проверяет успешное выполнение запросов из queries.sql."""
    db_file = tmp_path / "test_queries.sqlite"
    import_data(db_path=db_file)

    queries_path = BASE_DIR / "sql" / "queries.sql"
    with open(queries_path, "r", encoding="utf-8") as f:
        content = f.read()

    statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]

    conn = get_connection(db_file)
    try:
        for stmt in statements:
            lines = [
                line
                for line in stmt.splitlines()
                if not line.strip().startswith("--")
            ]
            clean_query = "\n".join(lines).strip()
            if clean_query:
                cursor = conn.execute(clean_query)
                assert cursor.fetchall() is not None
    finally:
        conn.close()
