"""Корневой конфигуратор URL-маршрутов проекта."""

from django.urls import include, path

urlpatterns = [
    path("", include("homepage.urls")),
    path("items/", include("items.urls")),
    path("requests/", include("item_requests.urls")),
]

handler404 = "homepage.views.custom_page_not_found"
