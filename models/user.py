"""Модуль модели пользователя."""

from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from models.item import Item
    from models.item_request import ItemRequest


class Sex(Enum):
    """Перечисление полов пользователя."""

    MALE = 0
    FEMALE = 1

    def label(self) -> str:
        """Возвращает человекочитаемое наименование пола."""
        return "Мужской" if self == Sex.MALE else "Женский"


class User:
    """Класс пользователя площадки совместного использования."""

    def __init__(
        self,
        name: str,
        age: int | None = None,
        sex: Sex | None = None,
        user_id: int | None = None,
    ) -> None:
        """Инициализация объекта пользователя."""
        self.id: int | None = user_id
        self.name: str = name
        self.age: int | None = age
        self.sex: Sex | None = sex
        self.items: list[Item] = []
        self.requests: list[ItemRequest] = []

    def __str__(self) -> str:
        """Строковое представление пользователя."""
        sex_str = self.sex.label() if self.sex else "Не указан"
        age_str = (
            f"{self.age} лет"
            if self.age is not None
            else "возраст не указан"
        )
        return (
            f"Пользователь {self.name} (ID: {self.id}, "
            f"{age_str}, {sex_str})"
        )

    def __repr__(self) -> str:
        """Служебное строковое представление."""
        return f"<User id={self.id} name='{self.name}'>"

    def __get_age__(self) -> int:
        """Запрашивает возраст пользователя с валидацией ввода."""
        while True:
            try:
                age = int(input("Введите возраст: "))
                if 0 < age <= 100:
                    return age
                print("Возраст должен быть числом от 1 до 100")
            except ValueError:
                print("Ошибка: возраст должен быть целым числом")

    def __get_sex__(self) -> Sex:
        """Запрашивает пол пользователя с валидацией ввода."""
        while True:
            try:
                value = int(
                    input("Введите ваш пол. 0 = Мужской, 1 = Женский: ")
                )
                if value == 0:
                    return Sex.MALE
                if value == 1:
                    return Sex.FEMALE
                print("Пол должен указываться числом 0 или 1")
            except ValueError:
                print("Ошибка: введите 0 или 1")

    def login(self) -> None:
        """Выводит приветственное сообщение при входе."""
        print(f"\n{self.name}, Добро пожаловать")

    def register(self) -> bool:
        """Регистрирует пользователя, запрашивая возраст и пол."""
        self.age = self.__get_age__()
        self.sex = self.__get_sex__()
        all_users.append(self)
        return True

    def to_dict(self) -> dict[str, Any]:
        """Преобразует объект пользователя в словарь для сериализации."""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "sex": self.sex.value if self.sex is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        """Создает объект пользователя из словаря."""
        sex = Sex(data["sex"]) if data.get("sex") is not None else None
        return cls(
            name=data["name"],
            age=data.get("age"),
            sex=sex,
            user_id=data.get("id"),
        )


all_users: list[User] = []
