"""Модуль работы с JSON-хранилищем проекта."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from models.item import Item
from models.item_request import ItemRequest, ItemRequestStatus
from models.transfer import Transfer
from models.user import Sex, User

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

USERS_FILE = DATA_DIR / "users.json"
ITEMS_FILE = DATA_DIR / "items.json"
REQUESTS_FILE = DATA_DIR / "requests.json"
TRANSFERS_FILE = DATA_DIR / "transfers.json"


def ensure_data_dir() -> None:
    """Создает директорию данных, если она отсутствует."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(file_path: Path) -> list[dict[str, Any]]:
    """Безопасно загружает список словарей из JSON-файла."""
    ensure_data_dir()
    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError) as err:
        print(f"Ошибка чтения файла {file_path.name}: {err}")
        return []


def save_json(file_path: Path, data: list[dict[str, Any]]) -> bool:
    """Сохраняет список словарей в JSON-файл через контекстный менеджер."""
    ensure_data_dir()
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError as err:
        print(f"Ошибка записи в файл {file_path.name}: {err}")
        return False


def load_users() -> list[User]:
    """Загружает список пользователей из JSON."""
    raw_users = load_json(USERS_FILE)
    users: list[User] = []
    for item in raw_users:
        user = User.from_dict(item)
        users.append(user)
    return users


def save_users(users: list[User]) -> bool:
    """Сохраняет список пользователей в JSON."""
    data = [u.to_dict() for u in users]
    return save_json(USERS_FILE, data)


def load_items(users_by_id: dict[int, User] | None = None) -> list[Item]:
    """Загружает список предметов и восстанавливает связь с владельцем."""
    raw_items = load_json(ITEMS_FILE)
    items: list[Item] = []
    for raw in raw_items:
        item = Item.from_dict(raw)
        owner_id = raw.get("owner_id")
        if owner_id and users_by_id and owner_id in users_by_id:
            item.own(users_by_id[owner_id])
        items.append(item)
    return items


def save_items(items: list[Item]) -> bool:
    """Сохраняет список предметов в JSON."""
    data = [item.to_dict() for item in items]
    return save_json(ITEMS_FILE, data)


def load_requests(
    items_by_id: dict[int, Item],
    users_by_id: dict[int, User],
) -> list[ItemRequest]:
    """Загружает список запросов и восстанавливает связи с объектами."""
    raw_requests = load_json(REQUESTS_FILE)
    requests: list[ItemRequest] = []

    for raw in raw_requests:
        item_id = raw.get("item_id")
        old_user_id = raw.get("old_user_id")
        new_user_id = raw.get("new_user_id")

        if (
            item_id in items_by_id
            and old_user_id in users_by_id
            and new_user_id in users_by_id
        ):
            status = ItemRequestStatus.from_string(
                raw.get("status", "PENDING")
            )
            req = ItemRequest(
                item=items_by_id[item_id],
                old_user=users_by_id[old_user_id],
                new_user=users_by_id[new_user_id],
                status=status,
                request_id=raw.get("id"),
                created_at=raw.get("created_at"),
            )
            requests.append(req)

    return requests


def save_requests(requests: list[ItemRequest]) -> bool:
    """Сохраняет список запросов в JSON."""
    data = [req.to_dict() for req in requests]
    return save_json(REQUESTS_FILE, data)


def load_transfers(
    items_by_id: dict[int, Item],
    users_by_id: dict[int, User],
) -> list[Transfer]:
    """Загружает историю передач и восстанавливает связи с объектами."""
    raw_transfers = load_json(TRANSFERS_FILE)
    transfers: list[Transfer] = []

    for raw in raw_transfers:
        transfer = Transfer.from_dict(raw)
        if transfer.item_id in items_by_id:
            transfer.item = items_by_id[transfer.item_id]
        if transfer.from_user_id in users_by_id:
            transfer.from_user = users_by_id[transfer.from_user_id]
        if transfer.to_user_id in users_by_id:
            transfer.to_user = users_by_id[transfer.to_user_id]
        transfers.append(transfer)

    return transfers


def save_transfers(transfers: list[Transfer]) -> bool:
    """Сохраняет историю передач предметов в JSON."""
    data = [t.to_dict() for t in transfers]
    return save_json(TRANSFERS_FILE, data)


def init_default_data() -> tuple[
    list[User], list[Item], list[ItemRequest], list[Transfer]
]:
    """Создает начальный набор демонстрационных данных при первом запуске."""
    u1 = User("Алексей Зубков", age=21, sex=Sex.MALE, user_id=1)
    u2 = User("Елена Смирнова", age=20, sex=Sex.FEMALE, user_id=2)
    u3 = User("Иван Ковалев", age=22, sex=Sex.MALE, user_id=3)
    users = [u1, u2, u3]

    it1 = Item(
        name="Электрический чайник",
        owner=u1,
        item_id=1,
        description="Чайник Bosch на 1.7 л, отлично кипятит воду для чая.",
    )
    it2 = Item(
        name="Утюг с отпаривателем",
        owner=u2,
        item_id=2,
        description="Компактный утюг для глажки одежды перед парами.",
    )
    it3 = Item(
        name="Ударная дрель",
        owner=u3,
        item_id=3,
        description="Дрель Makita для хозяйственных нужд и сборки мебели.",
    )
    it4 = Item(
        name="Микроволновая печь",
        owner=None,
        item_id=4,
        description="Общая микроволновка на этаже, сейчас свободна.",
    )
    items = [it1, it2, it3, it4]

    req1 = ItemRequest(
        item=it1,
        old_user=u1,
        new_user=u2,
        status=ItemRequestStatus.APPROVED,
        request_id=1,
        created_at="2026-10-10 12:00:00",
    )
    req2 = ItemRequest(
        item=it2,
        old_user=u2,
        new_user=u3,
        status=ItemRequestStatus.PENDING,
        request_id=2,
        created_at="2026-10-12 18:30:00",
    )
    requests = [req1, req2]

    tr1 = Transfer(
        item_id=1,
        from_user_id=1,
        to_user_id=2,
        transfer_id=1,
        transferred_at="2026-10-10 12:05:00",
        item=it1,
        from_user=u1,
        to_user=u2,
    )
    transfers = [tr1]

    save_users(users)
    save_items(items)
    save_requests(requests)
    save_transfers(transfers)

    return users, items, requests, transfers


def load_all_data() -> tuple[
    list[User], list[Item], list[ItemRequest], list[Transfer]
]:
    """Загружает все данные приложения, инициализируя их при отсутствии."""
    users = load_users()
    if not users:
        return init_default_data()

    users_by_id = {u.id: u for u in users if u.id is not None}
    items = load_items(users_by_id)
    items_by_id = {i.id: i for i in items if i.id is not None}

    requests = load_requests(items_by_id, users_by_id)
    transfers = load_transfers(items_by_id, users_by_id)

    return users, items, requests, transfers
