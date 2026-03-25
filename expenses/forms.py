"""Expenses forms — TransactionForm and CategoryForm."""

from django import forms

from .models import Category, Transaction


class TransactionForm(forms.ModelForm):
    """Form to add/edit a transaction (income or expense)."""

    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = Transaction
        fields = [
            "transaction_type",
            "amount",
            "category",
            "date",
            "description",
            "notes",
            "payment_method",
            "is_recurring",
        ]
        widgets = {
            "transaction_type": forms.Select(attrs={"class": "form-select", "id": "id_transaction_type"}),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01", "min": "0.01"}
            ),
            "category": forms.Select(attrs={"class": "form-select", "id": "id_category"}),
            "description": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Short description (e.g. Monthly rent)"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Additional notes (optional)"}
            ),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "is_recurring": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["category"].queryset = Category.get_for_user(user)
        self.fields["category"].empty_label = "— Select Category —"
        self.fields["amount"].label = "Amount (₹)"


class CategoryForm(forms.ModelForm):
    """Form to create or edit a custom category."""

    class Meta:
        model = Category
        fields = ["name", "icon", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Groceries"}),
            "icon": forms.Select(attrs={"class": "form-select"}),
            "color": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["icon"].choices = Category.ICON_CHOICES
        self.fields["color"].choices = Category.COLOR_CHOICES


class TransactionFilterForm(forms.Form):
    """Form to filter/search the transaction list."""

    query = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Search…"})
    )
    transaction_type = forms.ChoiceField(
        required=False,
        choices=[("", "All Types"), ("INCOME", "Income"), ("EXPENSE", "Expense")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.none(),
        empty_label="All Categories",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["category"].queryset = Category.get_for_user(user)
