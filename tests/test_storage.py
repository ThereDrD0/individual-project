"""Тесты хранилища данных JSON (ПР2 и ПР3)."""

import storage


def test_storage_load_and_save_json(tmp_path):
    """Проверка записи и чтения JSON через вспомогательные функции."""
    test_file = tmp_path / "test.json"
    data = [{"id": 1, "name": "Тест"}]
    assert storage.save_json(test_file, data)
    loaded = storage.load_json(test_file)
    assert loaded == data


def test_storage_load_nonexistent(tmp_path):
    """Проверка поведения при чтении несуществующего файла."""
    test_file = tmp_path / "absent.json"
    loaded = storage.load_json(test_file)
    assert loaded == []


def test_storage_load_corrupted_json(tmp_path):
    """Проверка обработки некорректного JSON."""
    test_file = tmp_path / "broken.json"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("{invalid json...")
    loaded = storage.load_json(test_file)
    assert loaded == []


def test_storage_load_all_data():
    """Проверка комплексной загрузки всех данных проекта."""
    users, items, requests, transfers = storage.load_all_data()
    assert len(users) >= 3
    assert len(items) >= 4
    assert len(requests) >= 2
    assert len(transfers) >= 1

    # Проверка восстановления связей
    user_ids = {u.id for u in users}
    for item in items:
        if item.owner:
            assert item.owner.id in user_ids
