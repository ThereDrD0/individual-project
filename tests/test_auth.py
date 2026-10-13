"""Тесты аутентификации и регистрации пользователей."""

from users import Sex, User, all_users


def test_user_registerable(monkeypatch):
    """Проверка успешной регистрации пользователя."""
    all_users.clear()
    inputs = iter(["11", "0"])  # age, sex
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))

    user = User("test_user")
    assert user.register()
    assert all_users.count(user) == 1


def test_age_validation_works_well(monkeypatch):
    """Проверка валидации возраста пользователя."""
    user = User("test_user")

    inputs = iter(["-100", "0", "125", "33"])
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))

    assert user.__get_age__() == 33


def test_sex_validation_works_well(monkeypatch):
    """Проверка валидации пола пользователя."""
    user = User("test_user")

    inputs = iter(["-1", "2", "-2", "0"])
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))

    assert user.__get_sex__() == Sex.MALE
