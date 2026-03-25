"""Expenses admin — register models for the Django admin panel."""

from django.contrib import admin

from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "icon", "color", "user"]
    list_filter = ["user"]
    search_fields = ["name"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "transaction_type", "amount", "category", "date", "payment_method"]
    list_filter = ["transaction_type", "category", "payment_method", "date"]
    search_fields = ["description", "notes"]
    date_hierarchy = "date"
