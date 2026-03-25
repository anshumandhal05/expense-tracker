"""Budgets admin."""

from django.contrib import admin

from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["user", "category", "monthly_limit", "month", "year"]
    list_filter = ["month", "year", "user"]
