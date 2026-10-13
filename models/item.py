"""Модуль модели предмета/вещи."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from models.user import User


class Item:
    """Класс предмета, доступного для совместного использования."""

    def __init__(
        self,
        name: str,
        owner: User | None = None,
        item_id: int | None = None,
        description: str = "",
    ) -> None:
        """Инициализация предмета."""
        self.id: int | None = item_id
        self.name: str = name
        self.description: str = description
        self.owner: User | None = None

        if owner is not None:
            self.own(owner)

    def __str__(self) -> str:
        """Строковое представление предмета."""
        status = f"у {self.owner.name}" if self.owner else "свободен"
        return f"Предмет '{self.name}' (ID: {self.id}, статус: {status})"

    def __repr__(self) -> str:
        """Служебное строковое представление."""
        owner_name = self.owner.name if self.owner else None
        return f"<Item id={self.id} name='{self.name}' owner='{owner_name}'>"

    def own(self, user: User) -> bool:
        """Закрепляет предмет за указанным пользователем."""
        if self.owner is not None and self.owner != user:
            print(
                f"Вещь '{self.name}' уже занята пользователем "
                f"{self.owner.name}"
            )
            return False

        self.owner = user
        if self not in user.items:
            user.items.append(self)

        print(f"Вещь {self.name} успешно занята вами, {user.name}")
        return True

    def free(self) -> None:
        """Освобождает предмет от текущего владельца."""
        if self.owner is None:
            return

        if self in self.owner.items:
            self.owner.items.remove(self)

        former_name = self.owner.name
        self.owner = None
        print(f"Вещь {self.name} успешно освобождена (ранее у {former_name})")

    def to_dict(self) -> dict[str, Any]:
        """Преобразует предмет в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner.id if self.owner else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Item:
        """Создает предмет из словаря (без привязанного владельца)."""
        return cls(
            name=data["name"],
            item_id=data.get("id"),
            description=data.get("description", ""),
        )
