"""Маршруты приложения item_requests."""

from django.urls import path
from item_requests import views

app_name = "item_requests"

urlpatterns = [
    path("", views.request_list, name="list"),
    path("<int:request_id>/", views.request_detail, name="detail"),
]
