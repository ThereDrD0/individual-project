"""Автоматизированные тесты маршрутов и веб-страниц Django (ПР5, 6, 7)."""

import os
import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sharing_platform.settings")
django.setup()


def test_homepage_view():
    """Тест отображения главной страницы."""
    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    text = response.content.decode("utf-8")
    assert "Площадка совместного использования" in text
    assert "Каталог вещей" in text


def test_items_list_view():
    """Тест каталога вещей и фильтрации."""
    client = Client()
    response = client.get("/items/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Каталог вещей" in content
    assert "Электрический чайник" in content

    # Тест фильтрации по свободным вещам
    res_free = client.get("/items/?status=free")
    assert res_free.status_code == 200

    # Тест фильтрации по занятым вещам
    res_busy = client.get("/items/?status=busy")
    assert res_busy.status_code == 200


def test_item_detail_view_found():
    """Тест страницы существующего предмета."""
    client = Client()
    response = client.get("/items/1/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Электрический чайник" in content
    assert "Алексей Зубков" in content


def test_item_detail_view_not_found():
    """Тест ошибки 404 при запросе несуществующего предмета."""
    client = Client()
    response = client.get("/items/99999/")
    assert response.status_code == 404


def test_requests_list_view():
    """Тест списка запросов и истории передач."""
    client = Client()
    response = client.get("/requests/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Запросы на получение вещей" in content
    assert "История состоявшихся передач" in content


def test_request_detail_view_found():
    """Тест существующего запроса."""
    client = Client()
    response = client.get("/requests/1/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Запрос на вещь #1" in content


def test_request_detail_view_not_found():
    """Тест ошибки 404 при запросе несуществующего запроса."""
    client = Client()
    response = client.get("/requests/99999/")
    assert response.status_code == 404


def test_available_items_view():
    """Тест страницы поиска свободных вещей и фильтрации по q."""
    client = Client()
    response = client.get("/items/available/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Поиск свободных вещей" in content

    # Поиск существующей свободной вещи
    res_search = client.get("/items/available/?q=Тостер")
    assert res_search.status_code == 200
    assert "Тостер Philips" in res_search.content.decode("utf-8")

    # Поиск несуществующей вещи
    res_empty = client.get("/items/available/?q=НесуществующаяВещь123")
    assert res_empty.status_code == 200
    assert "Свободные предметы не найдены" in res_empty.content.decode("utf-8")


def test_statistics_view():
    """Тест страницы статистики и аналитики заявок."""
    client = Client()
    response = client.get("/requests/statistics/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Статистика сервиса" in content
    assert "Популярность предметов" in content
    assert "Предметы с активным спросом" in content
