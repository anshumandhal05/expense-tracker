"""Budgets forms."""

from django import forms
from django.utils import timezone

from expenses.models import Category

from .models import Budget


class BudgetForm(forms.ModelForm):
    """Form to create or edit a budget."""

    MONTH_CHOICES = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]

    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    year = forms.IntegerField(
        min_value=2020, max_value=2100, widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Budget
        fields = ["category", "monthly_limit", "month", "year"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "monthly_limit": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01", "min": "1"}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["category"].queryset = Category.get_for_user(user)
        self.fields["category"].empty_label = "— Overall (no category filter) —"
        # Default to current month/year
        now = timezone.now()
        if not self.instance.pk:
            self.fields["month"].initial = now.month
            self.fields["year"].initial = now.year
        self.fields["monthly_limit"].label = "Budget Limit (₹)"
