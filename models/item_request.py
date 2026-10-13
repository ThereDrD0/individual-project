"""Модуль модели запроса на предмет."""

from __future__ import annotations
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from models.item import Item
    from models.user import User


class ItemRequestStatus(Enum):
    """Статусы запроса на совместное использование."""

    PENDING = "В ожидании"
    APPROVED = "Одобрен"
    REJECTED = "Отклонен"

    @classmethod
    def from_string(cls, value: str) -> ItemRequestStatus:
        """Получает статус из строкового значения или имени перечисления."""
        for status in cls:
            if status.name == value or status.value == value:
                return status
        return cls.PENDING


class ItemRequest:
    """Класс запроса на получение вещи от одного пользователя другому."""

    def __init__(
        self,
        item: Item,
        old_user: User,
        new_user: User,
        status: ItemRequestStatus = ItemRequestStatus.PENDING,
        request_id: int | None = None,
        created_at: str | None = None,
    ) -> None:
        """Инициализация запроса на предмет."""
        self.id: int | None = request_id
        self.item: Item = item
        self.old_user: User = old_user
        self.new_user: User = new_user
        self.status: ItemRequestStatus = status

        if created_at is not None:
            self.created_at: str = created_at
        else:
            self.created_at = datetime.now(UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        if self not in self.new_user.requests:
            self.new_user.requests.append(self)

    def __str__(self) -> str:
        """Строковое представление запроса."""
        return (
            f"Запрос #{self.id}: '{self.item.name}' "
            f"от {self.new_user.name} к {self.old_user.name} "
            f"[{self.status.value}] ({self.created_at})"
        )

    def __repr__(self) -> str:
        """Служебное строковое представление."""
        return (
            f"<ItemRequest id={self.id} item='{self.item.name}' "
            f"from='{self.new_user.name}' status='{self.status.name}'>"
        )

    def try_accept(self) -> bool:
        """Принимает запрос и передает вещь новому владельцу."""
        if self.status != ItemRequestStatus.PENDING:
            msg = (
                f"Запрос #{self.id} уже обработан "
                f"со статусом {self.status.value}"
            )
            print(msg)
            return False

        if self.item.owner is None:
            print(
                "Ошибка: у предмета нет текущего владельца, "
                "прямая передача невозможна."
            )
            return False

        if self.item.owner != self.old_user:
            print(
                f"Ошибка: владелец предмета изменился! "
                f"Текущий владелец: {self.item.owner.name}"
            )
            return False

        self.item.free()
        self.item.own(self.new_user)
        self.status = ItemRequestStatus.APPROVED
        print(
            f"Запрос #{self.id} успешно одобрен. "
            f"Вещь передана {self.new_user.name}."
        )
        return True

    def reject(self) -> bool:
        """Отклоняет запрос на передачу вещи."""
        if self.status != ItemRequestStatus.PENDING:
            print(f"Запрос #{self.id} уже обработан.")
            return False

        self.status = ItemRequestStatus.REJECTED
        print(f"Запрос #{self.id} отклонен владельцем.")
        return True

    def to_dict(self) -> dict[str, Any]:
        """Преобразует запрос в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "item_id": self.item.id,
            "old_user_id": self.old_user.id,
            "new_user_id": self.new_user.id,
            "status": self.status.name,
            "created_at": self.created_at,
        }
