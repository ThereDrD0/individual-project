"""Модуль модели истории передачи предметов."""

from __future__ import annotations
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from models.item import Item
    from models.user import User


class Transfer:
    """Класс записи о состоявшейся передаче предмета."""

    def __init__(
        self,
        item_id: int,
        from_user_id: int,
        to_user_id: int,
        transfer_id: int | None = None,
        transferred_at: str | None = None,
        item: Item | None = None,
        from_user: User | None = None,
        to_user: User | None = None,
    ) -> None:
        """Инициализация записи о передаче."""
        self.id: int | None = transfer_id
        self.item_id: int = item_id
        self.from_user_id: int = from_user_id
        self.to_user_id: int = to_user_id
        self.item: Item | None = item
        self.from_user: User | None = from_user
        self.to_user: User | None = to_user

        if transferred_at is not None:
            self.transferred_at: str = transferred_at
        else:
            self.transferred_at = datetime.now(UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    def __str__(self) -> str:
        """Строковое представление записи о передаче."""
        item_name = self.item.name if self.item else f"ID {self.item_id}"
        from_name = (
            self.from_user.name
            if self.from_user
            else f"ID {self.from_user_id}"
        )
        to_name = (
            self.to_user.name
            if self.to_user
            else f"ID {self.to_user_id}"
        )
        return (
            f"Передача #{self.id}: '{item_name}' "
            f"от {from_name} к {to_name} ({self.transferred_at})"
        )

    def __repr__(self) -> str:
        """Служебное строковое представление."""
        return (
            f"<Transfer id={self.id} item_id={self.item_id} "
            f"from={self.from_user_id} to={self.to_user_id}>"
        )

    def to_dict(self) -> dict[str, Any]:
        """Преобразует запись в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "item_id": self.item_id,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "transferred_at": self.transferred_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transfer:
        """Создает запись о передаче из словаря."""
        return cls(
            item_id=data["item_id"],
            from_user_id=data["from_user_id"],
            to_user_id=data["to_user_id"],
            transfer_id=data.get("id"),
            transferred_at=data.get("transferred_at"),
        )
