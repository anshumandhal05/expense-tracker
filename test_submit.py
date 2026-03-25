import os

import django
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_project.settings")
django.setup()

User = get_user_model()
user, _ = User.objects.get_or_create(username="testuser")
user.set_password("testpass123")
user.save()

client = Client()
client.login(username="testuser", password="testpass123")

from expenses.models import Category

cat, _ = Category.objects.get_or_create(user=user, name="Groceries", type="EXPENSE")

# Test POST expense
response = client.post(
    reverse("transaction_add") + "?type=EXPENSE",
    {
        "transaction_type": "EXPENSE",
        "amount": "100.50",
        "category": cat.id,
        "date": "2026-03-18",
        "description": "Test",
        "payment_method": "CASH",
    },
)

print(f"Transaction add POST status: {response.status_code}")
if response.status_code == 500:
    print("Error on POST transaction")

# check if it created
from expenses.models import Transaction

print("Transactions count:", Transaction.objects.filter(user=user).count())
