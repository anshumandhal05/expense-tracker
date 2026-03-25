"""Management command to seed default expense/income categories."""

from django.core.management.base import BaseCommand

from expenses.models import Category

DEFAULTS = [
    ("Food & Dining", "fa-utensils", "#f97316"),
    ("Travel", "fa-plane", "#3b82f6"),
    ("Bills & Utilities", "fa-bolt", "#eab308"),
    ("Shopping", "fa-shopping-bag", "#8b5cf6"),
    ("Health", "fa-heartbeat", "#ef4444"),
    ("Education", "fa-graduation-cap", "#06b6d4"),
    ("Entertainment", "fa-film", "#ec4899"),
    ("Transport", "fa-car", "#0ea5e9"),
    ("Housing", "fa-home", "#6366f1"),
    ("Salary", "fa-briefcase", "#10b981"),
    ("Freelance", "fa-laptop", "#14b8a6"),
    ("Gifts", "fa-gift", "#f43f5e"),
    ("Investment", "fa-chart-line", "#84cc16"),
    ("Other", "fa-ellipsis-h", "#94a3b8"),
]


class Command(BaseCommand):
    help = "Seed the database with default categories"

    def handle(self, *args, **options):
        created = 0
        for name, icon, color in DEFAULTS:
            _, was_created = Category.objects.get_or_create(
                name=name, user=None, defaults={"icon": icon, "color": color}
            )
            if was_created:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(f"Seeded {created} new default categories ({len(DEFAULTS) - created} already existed).")
        )
