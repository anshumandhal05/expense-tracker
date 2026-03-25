"""Expenses app — Transaction and Category models."""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Expense/Income category — system defaults (user=None) + user-created custom ones."""

    ICON_CHOICES = [
        ("fa-utensils", "Food & Dining"),
        ("fa-plane", "Travel"),
        ("fa-bolt", "Bills & Utilities"),
        ("fa-shopping-bag", "Shopping"),
        ("fa-heartbeat", "Health"),
        ("fa-graduation-cap", "Education"),
        ("fa-film", "Entertainment"),
        ("fa-car", "Transport"),
        ("fa-home", "Housing"),
        ("fa-briefcase", "Salary"),
        ("fa-laptop", "Freelance"),
        ("fa-gift", "Gifts"),
        ("fa-chart-line", "Investment"),
        ("fa-ellipsis-h", "Other"),
    ]
    COLOR_CHOICES = [
        ("#6366f1", "Indigo"),
        ("#f59e0b", "Amber"),
        ("#10b981", "Emerald"),
        ("#ef4444", "Red"),
        ("#3b82f6", "Blue"),
        ("#8b5cf6", "Purple"),
        ("#14b8a6", "Teal"),
        ("#f97316", "Orange"),
        ("#84cc16", "Lime"),
        ("#06b6d4", "Cyan"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, help_text="Null means system-wide default category"
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default="fa-ellipsis-h")
    color = models.CharField(max_length=20, default="#6366f1")

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @classmethod
    def get_for_user(cls, user):
        """Return system categories + this user's custom categories."""
        return cls.objects.filter(models.Q(user=user) | models.Q(user=None))


class Transaction(models.Model):
    """Unified model for both income and expense transactions."""

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TYPE_CHOICES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]
    PAYMENT_CHOICES = [
        ("CASH", "Cash"),
        ("CARD", "Card"),
        ("BANK", "Bank Transfer"),
        ("UPI", "UPI / Digital Wallet"),
        ("OTHER", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=EXPENSE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions"
    )
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="CARD")
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} — ₹{self.amount} on {self.date}"
