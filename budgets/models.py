"""Budgets models — per-category monthly spending limits."""

from django.contrib.auth.models import User
from django.db import models

from expenses.models import Category


class Budget(models.Model):
    """Monthly budget limit for a specific category."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets",
        null=True,
        blank=True,
        help_text="Null = overall budget (no specific category)",
    )
    monthly_limit = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.PositiveSmallIntegerField()  # 1–12
    year = models.PositiveIntegerField()

    class Meta:
        unique_together = ["user", "category", "month", "year"]
        ordering = ["-year", "-month", "category__name"]

    def __str__(self):
        cat_name = self.category.name if self.category else "Overall"
        return f"{cat_name} — {self.month}/{self.year} — Limit: ₹{self.monthly_limit}"

    def get_spent(self):
        """Return the amount spent in this budget's category/month/year."""
        from django.db.models import Sum

        from expenses.models import Transaction

        qs = Transaction.objects.filter(
            user=self.user,
            transaction_type="EXPENSE",
            date__month=self.month,
            date__year=self.year,
        )
        if self.category:
            qs = qs.filter(category=self.category)
        result = qs.aggregate(total=Sum("amount"))["total"] or 0
        return result

    def get_remaining(self):
        return self.monthly_limit - self.get_spent()

    def get_percentage(self):
        if self.monthly_limit == 0:
            return 0
        pct = (self.get_spent() / self.monthly_limit) * 100
        return min(round(pct, 1), 100)

    def is_exceeded(self):
        return self.get_spent() > self.monthly_limit
