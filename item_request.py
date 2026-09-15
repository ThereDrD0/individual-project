from datetime import UTC, datetime
from enum import Enum, auto

from items import Item
from users import User


class ItemRequestStatus(Enum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()


class ItemRequest:
    def __init__(
        self,
        item: Item,
        new_user: User,
        status: ItemRequestStatus = ItemRequestStatus.PENDING,
    ):
        self.item = item
        self.new_user = new_user
        self.time = datetime.now(UTC)
        self.status = status

    def try_accept(self) -> bool:
        if self.item.owner is None:
            print(
                "Ошибка - попытка принять принять запрос с предметом, у которого нет владельца"
            )
            return False

        self.item.free()
        self.item.own(self.new_user)

        return True
