"""Expenses URL configuration."""

from django.urls import path

from . import views

urlpatterns = [
    # Transactions
    path("", views.transaction_list, name="transaction_list"),
    path("add/", views.transaction_add, name="transaction_add"),
    path("<int:pk>/edit/", views.transaction_edit, name="transaction_edit"),
    path("<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
    # Categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_add, name="category_add"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
]
