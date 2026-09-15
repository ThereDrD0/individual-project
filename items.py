from users import User


class Item:
    def __init__(self, name: str, owner: User | None):
        self.name = name
        self.owner = owner

    def own(self, user: User):
        if self.owner is not None:
            print(f"Вещь уже занята {self.owner.name}")
            return

        self.owner = user
        print(f"Вещь {self.name} успешна занята вами, {user.name}")

    def free(self):
        if self.owner is None:
            return

        self.owner = None
        print(f"Вещь {self.name} успешно освобождена")

items: list[Item] = []

def register_new_item(user: User):
    name = input("Введите название предмета: ")
    item = Item(name, user)

    items.append(item)

def get_item_names(user: User | None = None) -> str:

    avaliable_items = get_all_items(user)

    if len(avaliable_items) <= 0:
        return "Нет предметов"
    else:
        message = "\nДоступные предметы:\n"
        return message + "\n".join(item.name for item in avaliable_items)

def get_all_items(user: User | None = None) -> list[Item]:
    if user is None:
        return items
    
    owned = []
    for item in items:
        if item.owner == user:
            owned.append(item)

    return owned

def transfer_item(owner:User, recipient:User, item: Item | None) -> bool:
    if item is None:
        avaliable_items = get_all_items(owner)
        if len(avaliable_items) == 0:
            print("У вас нет предметов для передачи")
            return False
        
        selected_item_name = input(f"Введите название предмета, который хотите передать. Возможнные варианты: {get_item_names(owner)}\n")
        selected_item = None

        for possibleItem in avaliable_items:
            if possibleItem.name == selected_item_name:
                selected_item = possibleItem
                break
        
        if selected_item is None:
            print(f"Предмета с именем не {selected_item_name} найдено")
            return False

        selected_item.free()
        selected_item.own(recipient)
    
    return True



