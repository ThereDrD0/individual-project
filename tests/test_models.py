"""Тесты классов объектной модели предметной области (ПР3)."""

from models.item import Item
from models.item_request import ItemRequest, ItemRequestStatus
from models.transfer import Transfer
from models.user import Sex, User


def test_user_creation_and_str():
    """Тест создания и строкового представления пользователя."""
    user = User("Алексей", age=21, sex=Sex.MALE, user_id=1)
    assert user.name == "Алексей"
    assert user.age == 21
    assert user.sex == Sex.MALE
    assert "Алексей" in str(user)
    assert "21 лет" in str(user)
    assert "Мужской" in str(user)

    data = user.to_dict()
    assert data["id"] == 1
    assert data["name"] == "Алексей"
    assert data["sex"] == 0

    restored = User.from_dict(data)
    assert restored.id == 1
    assert restored.name == "Алексей"
    assert restored.sex == Sex.MALE


def test_item_own_and_free():
    """Тест закрепления и освобождения вещи."""
    user1 = User("Иван", age=22, sex=Sex.MALE, user_id=1)
    user2 = User("Мария", age=20, sex=Sex.FEMALE, user_id=2)

    item = Item("Утюг", owner=user1, item_id=10, description="Паровой")
    assert item.owner == user1
    assert item in user1.items
    assert "у Иван" in str(item)

    # Попытка занять уже занятый предмет другим пользователем
    res = item.own(user2)
    assert not res
    assert item.owner == user1

    # Освобождение предмета
    item.free()
    assert item.owner is None
    assert item not in user1.items
    assert "свободен" in str(item)

    # Закрепление за новым пользователем
    res = item.own(user2)
    assert res
    assert item.owner == user2
    assert item in user2.items


def test_item_request_lifecycle():
    """Тест создания, принятия и отклонения запроса на предмет."""
    owner = User("Владелец", age=25, sex=Sex.MALE, user_id=1)
    requester = User("Заявитель", age=23, sex=Sex.FEMALE, user_id=2)
    item = Item("Чайник", owner=owner, item_id=1)

    req = ItemRequest(
        item=item,
        old_user=owner,
        new_user=requester,
        request_id=100,
    )
    assert req.status == ItemRequestStatus.PENDING
    assert "В ожидании" in str(req)

    # Принятие запроса
    assert req.try_accept()
    assert req.status == ItemRequestStatus.APPROVED
    assert item.owner == requester
    assert item in requester.items
    assert item not in owner.items

    # Повторное принятие не должно сработать
    assert not req.try_accept()


def test_item_request_rejection():
    """Тест отклонения запроса."""
    owner = User("Владелец", age=25, sex=Sex.MALE, user_id=1)
    requester = User("Заявитель", age=23, sex=Sex.FEMALE, user_id=2)
    item = Item("Ноутбук", owner=owner, item_id=2)

    req = ItemRequest(
        item=item,
        old_user=owner,
        new_user=requester,
        request_id=101,
    )
    assert req.reject()
    assert req.status == ItemRequestStatus.REJECTED
    assert item.owner == owner


def test_transfer_creation():
    """Тест создания записи о передаче."""
    user1 = User("Алексей", user_id=1)
    user2 = User("Борис", user_id=2)
    item = Item("Книга", item_id=5)

    transfer = Transfer(
        item_id=5,
        from_user_id=1,
        to_user_id=2,
        transfer_id=1,
        item=item,
        from_user=user1,
        to_user=user2,
    )
    assert "Передача #1" in str(transfer)
    assert "Книга" in str(transfer)
    assert "Алексей" in str(transfer)
    assert "Борис" in str(transfer)

    data = transfer.to_dict()
    assert data["item_id"] == 5
    assert data["from_user_id"] == 1
    assert data["to_user_id"] == 2
