"""Конфигурация приложения items."""

from django.apps import AppConfig


class ItemsConfig(AppConfig):
    """Класс конфигурации приложения items."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "items"
    verbose_name = "Вещи и предметы"
