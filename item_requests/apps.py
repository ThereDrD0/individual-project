"""Конфигурация приложения item_requests."""

from django.apps import AppConfig


class ItemRequestsConfig(AppConfig):
    """Класс конфигурации приложения item_requests."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "item_requests"
    verbose_name = "Запросы и передачи предметов"
