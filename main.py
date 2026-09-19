from items import get_item_names, register_new_item
from users import User, all_users


def main():
    user = login()
    while True:
        do(user)


def login() -> User:
    name = input("Введите свое имя: ")
    
    user = None
    for maybeUser in all_users:
        if maybeUser.name != name:
            continue

        user = maybeUser
        break;

    if user is None:
        user = User(name)
        user.register()

    user.login()
    return user

def do(user: User):
    welcome = """
Выберите действие
1. Передать предмет
2. Запросить предмет
3. Зарегистрировать предмет
4. Получить список зарегистрированных предметов"""

    print(welcome)
    doing = 0
    while True:
        try:
            doing = int(input())
        except:
            print("Действие должно быть числом")
        break
    
    match(doing):
        case 1:
            pass
        case 2:
            pass
        case 3:
            register_new_item(user)
        case 4: 
            print(get_item_names())
        

main()
