"""Модуль инициализации и подключения к базе данных SQLite."""

from __future__ import annotations

from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sharing.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection(
    db_path: Path | str = DB_PATH,
) -> sqlite3.Connection:
    """Создает и настраивает соединение с SQLite базой данных."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(
    db_path: Path | str = DB_PATH,
    schema_path: Path | str = SCHEMA_PATH,
) -> None:
    """Инициализирует схему БД из SQL-файла."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
