from enum import Enum


class Sex(Enum):
    MALE = 0
    FEMALE = 1


class User:
    def __init__(self, name: str, age: int | None = None, sex: Sex | None = None):
        self.name = name
        self.age = age
        self.sex = sex

    def __get_age__(self) -> int:
        age = 0
        while True:
            age = int(input("Введите возраст: "))

            if 0 < age <= 100:
                break
            else:
                print("Возраст должен быть числом от 1 до 100")

        return age


    def __get_sex__(self) -> Sex:
        sex = Sex.MALE
        while True:
            potentialSex = int(input("Введите ваш пол. 0 = Мужской, 1 = Женский: "))

            if potentialSex == 1 or potentialSex == 0:
                break
            else:
                print("Пол должен указываться числом 0 или 1")
        
        return sex


    def login(self):
        print(f"\n{self.name}, Добро пожаловать")

    def register(self) -> bool:
        age = self.__get_age__()
        sex = self.__get_sex__()

        self.age = age
        self.sex = sex

        all_users.append(self)
        return True


all_users: list[User] = []
