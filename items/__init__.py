"""Пакет приложения items и функции работы с предметами."""

from __future__ import annotations
from models.item import Item
from models.user import User

items: list[Item] = []


def register_new_item(
    user: User,
    name: str | None = None,
    description: str = "",
) -> Item:
    """Регистрирует новый предмет и закрепляет его за пользователем."""
    if not name:
        name = input("Введите название предмета: ").strip()
    new_id = max((it.id for it in items if it.id), default=0) + 1
    item = Item(
        name=name,
        owner=user,
        item_id=new_id,
        description=description,
    )
    items.append(item)
    return item


def get_all_items(user: User | None = None) -> list[Item]:
    """Возвращает список всех предметов или предметов пользователя."""
    if user is None:
        return items

    return [item for item in items if item.owner == user]


def get_item_names(user: User | None = None) -> str:
    """Возвращает форматированную строку с именами доступных предметов."""
    available_items = get_all_items(user)

    if not available_items:
        return "Нет предметов"

    message = "\nДоступные предметы:\n"
    return message + "\n".join(item.name for item in available_items)


def transfer_item(
    owner: User, recipient: User, item: Item | None = None
) -> bool:
    """Передает предмет от одного пользователя другому."""
    if item is None:
        available_items = get_all_items(owner)
        if not available_items:
            print("У вас нет предметов для передачи")
            return False

        options = get_item_names(owner)
        prompt = (
            f"Введите название предмета для передачи. "
            f"Возможные варианты: {options}\n"
        )
        selected_item_name = input(prompt).strip()
        selected_item = None

        for possible_item in available_items:
            if possible_item.name == selected_item_name:
                selected_item = possible_item
                break

        if selected_item is None:
            print(f"Предмет с именем '{selected_item_name}' не найден")
            return False

        item = selected_item

    item.free()
    item.own(recipient)
    return True


__all__ = [
    "Item",
    "items",
    "register_new_item",
    "get_all_items",
    "get_item_names",
    "transfer_item",
]
