import os

import django
from django.contrib.auth import get_user_model
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_project.settings")
django.setup()

User = get_user_model()
user, created = User.objects.get_or_create(username="testuser")
if created:
    user.set_password("testpass123")
    user.save()

client = Client(HTTP_HOST="127.0.0.1")
client.login(username="testuser", password="testpass123")

urls_to_test = [
    "/",  # dashboard
    "/expenses/",  # transaction list
    "/expenses/add/",  # may require ?type=EXPENSE
    "/expenses/reports/",
    "/expenses/categories/",
    "/budgets/",
    "/accounts/profile/",
]

for url in urls_to_test:
    try:
        response = client.get(url)
        print(f"{url} -> status: {response.status_code}")
        if response.status_code == 500:
            print(f"ERROR 500 on {url}")
    except Exception as e:
        print(f"{url} -> EXCEPTION: {e}")
