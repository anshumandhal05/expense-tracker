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

client = Client(HTTP_HOST="127.0.0.1")
client.login(username="testuser", password="testpass123")

routes = [
    "dashboard",
    "reports",
    "export_csv",
    "export_pdf",
    "login",
    "register",
    "logout",
    "profile",
    "transaction_list",
    "transaction_add",
    "budget_list",
    "budget_add",
    "category_list",
    "category_add",
]

print("Testing all routes...")
for route in routes:
    try:
        url = reverse(route)
        response = client.get(url)
        print(f"[{response.status_code}] {url}")
        if response.status_code >= 400:
            print(f"   -> ERROR detail on {url}: status {response.status_code}")
    except Exception as e:
        print(f"EXCEPTION resolving/fetching {route}: {e}")
