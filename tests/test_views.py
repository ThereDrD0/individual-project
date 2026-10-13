"""Автоматизированные тесты маршрутов и веб-страниц Django (ПР5 и ПР6)."""

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
