"""Главный модуль консольного приложения проекта (ПР1–ПР3)."""

from __future__ import annotations
import sys

from models.item import Item
from models.item_request import ItemRequest, ItemRequestStatus
from models.transfer import Transfer
from models.user import User
import storage

users: list[User] = []
items: list[Item] = []
requests: list[ItemRequest] = []
transfers: list[Transfer] = []


def initialize_app() -> None:
    """Инициализирует данные приложения из хранилища."""
    global users, items, requests, transfers
    users, items, requests, transfers = storage.load_all_data()


def save_current_state() -> None:
    """Сохраняет текущее состояние приложения в файлы JSON."""
    storage.save_users(users)
    storage.save_items(items)
    storage.save_requests(requests)
    storage.save_transfers(transfers)
    print("Данные успешно сохранены в JSON.")


def login() -> User:
    """Выполняет вход или регистрацию пользователя."""
    print("\n--- ВХОД В СИСТЕМУ ---")
    if users:
        print("Существующие пользователи:")
        for idx, u in enumerate(users, start=1):
            print(f"  {idx}. {u.name} (ID: {u.id})")
        print("  0. Зарегистрировать нового пользователя")

        choice = input("Выберите номер или введите имя: ").strip()
        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(users):
                user = users[num - 1]
                user.login()
                return user

        for u in users:
            if u.name.lower() == choice.lower():
                u.login()
                return u

    name = input("Введите ваше имя: ").strip()
    while not name:
        name = input("Имя не может быть пустым. Введите имя: ").strip()

    new_id = max((u.id for u in users if u.id is not None), default=0) + 1
    new_user = User(name=name, user_id=new_id)
    new_user.register()
    users.append(new_user)
    save_current_state()
    new_user.login()
    return new_user


def view_catalog() -> None:
    """Выводит каталог всех вещей."""
    print("\n--- КАТАЛОГ ВЕЩЕЙ ---")
    if not items:
        print("Каталог пуст.")
        return

    for item in items:
        status = (
            f"находится у {item.owner.name}"
            if item.owner
            else "свободен для использования"
        )
        print(f"[{item.id}] {item.name} — {status}")
        if item.description:
            print(f"     Описание: {item.description}")


def register_item(current_user: User) -> None:
    """Регистрирует новую вещь и закрепляет её за пользователем."""
    print("\n--- ДОБАВЛЕНИЕ НОВОЙ ВЕЩИ ---")
    name = input("Введите название вещи: ").strip()
    if not name:
        print("Отмена: название не может быть пустым.")
        return

    desc = input("Введите краткое описание вещи: ").strip()
    new_id = max((it.id for it in items if it.id is not None), default=0) + 1
    new_item = Item(
        name=name,
        owner=current_user,
        item_id=new_id,
        description=desc,
    )
    items.append(new_item)
    save_current_state()
    print(f"Вещь '{name}' (ID: {new_id}) успешно добавлена в каталог.")


def request_item(current_user: User) -> None:
    """Создает запрос на вещь от другого пользователя."""
    print("\n--- ЗАПРОС ВЕЩИ ---")
    available_items = [
        it for it in items
        if it.owner is not None and it.owner != current_user
    ]

    if not available_items:
        print("Нет вещей у других пользователей, доступных для запроса.")
        return

    for it in available_items:
        print(f"[{it.id}] {it.name} (текущий владелец: {it.owner.name})")

    choice_str = input("Введите ID вещи для запроса: ").strip()
    if not choice_str.isdigit():
        print("ID должен быть числом.")
        return

    item_id = int(choice_str)
    target_item = next(
        (it for it in available_items if it.id == item_id), None
    )
    if not target_item or target_item.owner is None:
        print("Вещь с таким ID не найдена среди доступных.")
        return

    new_id = max((r.id for r in requests if r.id is not None), default=0) + 1
    new_req = ItemRequest(
        item=target_item,
        old_user=target_item.owner,
        new_user=current_user,
        status=ItemRequestStatus.PENDING,
        request_id=new_id,
    )
    requests.append(new_req)
    save_current_state()
    print(
        f"Запрос #{new_id} на '{target_item.name}' "
        f"успешно отправлен пользователю {target_item.owner.name}."
    )


def handle_incoming_requests(current_user: User) -> None:
    """Просматривает и обрабатывает входящие запросы текущего пользователя."""
    print("\n--- ВХОДЯЩИЕ ЗАПРОСЫ ---")
    incoming = [
        r for r in requests
        if r.old_user == current_user and r.status == ItemRequestStatus.PENDING
    ]

    if not incoming:
        print("У вас нет ожидающих подтверждения запросов.")
        return

    for r in incoming:
        print(
            f"[{r.id}] Запрос от {r.new_user.name} "
            f"на вещь '{r.item.name}' ({r.created_at})"
        )

    choice_str = input("Введите ID запроса для обработки (0 для отмены): ")
    if not choice_str.isdigit() or int(choice_str) == 0:
        return

    req_id = int(choice_str)
    req = next((r for r in incoming if r.id == req_id), None)
    if not req:
        print("Запрос с указанным ID не найден.")
        return

    action = input("1 — Одобрить и передать вещь, 2 — Отклонить: ").strip()
    if action == "1":
        old_owner = req.old_user
        new_owner = req.new_user
        target_item = req.item
        if req.try_accept():
            new_tr_id = (
                max((t.id for t in transfers if t.id is not None), default=0)
                + 1
            )
            transfer = Transfer(
                item_id=target_item.id or 0,
                from_user_id=old_owner.id or 0,
                to_user_id=new_owner.id or 0,
                transfer_id=new_tr_id,
                item=target_item,
                from_user=old_owner,
                to_user=new_owner,
            )
            transfers.append(transfer)
            save_current_state()
    elif action == "2":
        req.reject()
        save_current_state()
    else:
        print("Неизвестное действие.")


def view_my_items(current_user: User) -> None:
    """Выводит список вещей, находящихся у текущего пользователя."""
    print(f"\n--- ВЕЩИ ПОЛЬЗОВАТЕЛЯ {current_user.name} ---")
    my_items = [it for it in items if it.owner == current_user]
    if not my_items:
        print("У вас сейчас нет вещей на руках.")
        return

    for it in my_items:
        print(f"[{it.id}] {it.name} — {it.description or 'без описания'}")


def view_transfers() -> None:
    """Выводит историю передач вещей."""
    print("\n--- ИСТОРИЯ ПЕРЕДАЧ ---")
    if not transfers:
        print("История передач пока пуста.")
        return

    for t in transfers:
        print(str(t))


def process_input(current_user: User) -> bool:
    """Обрабатывает выбор действия пользователя из меню."""
    menu = """
Выберите действие:
1. Каталог всех вещей
2. Добавить новую вещь
3. Запросить вещь у соседа
4. Входящие запросы ко мне
5. Мои вещи
6. История передач
7. Сохранить данные
0. Выход
"""
    print(menu)
    choice = input("Ваш выбор: ").strip()

    match choice:
        case "1":
            view_catalog()
        case "2":
            register_item(current_user)
        case "3":
            request_item(current_user)
        case "4":
            handle_incoming_requests(current_user)
        case "5":
            view_my_items(current_user)
        case "6":
            view_transfers()
        case "7":
            save_current_state()
        case "0":
            print("До свидания!")
            return False
        case _:
            print("Некорректный пункт меню. Повторите попытку.")

    return True


def main() -> None:
    """Главная функция консольного приложения."""
    initialize_app()
    print("Добро пожаловать в сервис 'Площадка совместного использования'!")
    user = login()
    while True:
        try:
            if not process_input(user):
                break
        except (KeyboardInterrupt, EOFError):
            print("\nСеанс завершен.")
            sys.exit(0)


if __name__ == "__main__":
    main()
