"""Конфигурация приложения homepage."""

from django.apps import AppConfig


class HomepageConfig(AppConfig):
    """Класс конфигурации приложения homepage."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "homepage"
    verbose_name = "Главная страница"
