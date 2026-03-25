"""Core views — dashboard, Chart.js API, CSV/PDF export, reports."""

import json
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from budgets.models import Budget
from expenses.models import Transaction

from .utils import export_csv, export_pdf


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@login_required
def dashboard(request):
    """Main dashboard — totals, recent transactions, budget alerts, chart data."""
    now = timezone.now()
    today = now.date()
    current_month = today.month
    current_year = today.year

    # Initialize all chart data variables with defaults
    pie_labels = []
    pie_values = []
    pie_colors = []
    month_labels = []
    bar_income = []
    bar_expense = []

    # ── Overall totals ──
    total_income = Transaction.objects.filter(user=request.user, transaction_type="INCOME").aggregate(t=Sum("amount"))[
        "t"
    ] or Decimal("0")

    total_expense = Transaction.objects.filter(user=request.user, transaction_type="EXPENSE").aggregate(
        t=Sum("amount")
    )["t"] or Decimal("0")

    balance = total_income - total_expense

    # ── Monthly totals ──
    monthly_income = Transaction.objects.filter(
        user=request.user, transaction_type="INCOME", date__month=current_month, date__year=current_year
    ).aggregate(t=Sum("amount"))["t"] or Decimal("0")

    monthly_expense = Transaction.objects.filter(
        user=request.user, transaction_type="EXPENSE", date__month=current_month, date__year=current_year
    ).aggregate(t=Sum("amount"))["t"] or Decimal("0")

    # ── Recent transactions ──
    recent_transactions = (
        Transaction.objects.filter(user=request.user).select_related("category").order_by("-date", "-created_at")[:8]
    )

    # ── Budget alerts ──
    current_budgets = Budget.objects.filter(user=request.user, month=current_month, year=current_year).select_related(
        "category"
    )
    exceeded_budgets = [b for b in current_budgets if b.is_exceeded()]

    # ── Expense by category (for pie chart) ──
    category_data = (
        Transaction.objects.filter(
            user=request.user, transaction_type="EXPENSE", date__month=current_month, date__year=current_year
        )
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:8]
    )

    pie_labels = [d["category__name"] or "Uncategorized" for d in category_data]
    pie_values = [float(d["total"]) for d in category_data]
    pie_colors = [d["category__color"] or "#6366f1" for d in category_data]

    # ── Monthly income vs expense (last 6 months, bar chart) ──
    six_months_income = (
        Transaction.objects.filter(user=request.user, transaction_type="INCOME")
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    six_months_expense = (
        Transaction.objects.filter(user=request.user, transaction_type="EXPENSE")
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    # Build unified month list
    all_months_set = set()
    for row in six_months_income:
        all_months_set.add(row["month"].strftime("%b %Y"))
    for row in six_months_expense:
        all_months_set.add(row["month"].strftime("%b %Y"))

    income_by_month = {row["month"].strftime("%b %Y"): float(row["total"]) for row in six_months_income}
    expense_by_month = {row["month"].strftime("%b %Y"): float(row["total"]) for row in six_months_expense}

    month_labels = sorted(all_months_set, key=lambda m: datetime.strptime(m, "%b %Y"))[-12:]
    bar_income = [income_by_month.get(m, 0) for m in month_labels]
    bar_expense = [expense_by_month.get(m, 0) for m in month_labels]

    context = {
        # Totals
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        # Transactions
        "recent_transactions": recent_transactions,
        # Budget alerts
        "exceeded_budgets": exceeded_budgets,
        "exceeded_count": len(exceeded_budgets),
        "current_budgets": current_budgets[:4],  # Show up to 4 budgets on dashboard
        # Charts (pass as Python lists, let template handle JSON serialization)
        "pie_labels": pie_labels,
        "pie_values": pie_values,
        "pie_colors": pie_colors,
        "month_labels": month_labels,
        "bar_income": bar_income,
        "bar_expense": bar_expense,
    }
    return render(request, "core/dashboard.html", context)


@login_required
def reports_view(request):
    """Reports page — summary statistics and export options."""
    now = timezone.now()
    qs = Transaction.objects.filter(user=request.user).select_related("category")

    # Filter by month/year
    filter_month = request.GET.get("month", now.month)
    filter_year = request.GET.get("year", now.year)
    try:
        filter_month = int(filter_month)
        filter_year = int(filter_year)
    except (ValueError, TypeError):
        filter_month, filter_year = now.month, now.year

    filtered_qs = qs.filter(date__month=filter_month, date__year=filter_year)

    total_income = filtered_qs.filter(transaction_type="INCOME").aggregate(t=Sum("amount"))["t"] or 0
    total_expense = filtered_qs.filter(transaction_type="EXPENSE").aggregate(t=Sum("amount"))["t"] or 0

    top_categories = (
        filtered_qs.filter(transaction_type="EXPENSE")
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:5]
    )

    MONTH_NAMES = [
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    years = list(range(now.year - 3, now.year + 1))

    context = {
        "filter_month": filter_month,
        "filter_year": filter_year,
        "month_name": MONTH_NAMES[filter_month],
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "top_categories": top_categories,
        "months": [(i, MONTH_NAMES[i]) for i in range(1, 13)],
        "years": years,
    }
    return render(request, "core/reports.html", context)


@login_required
def export_csv_view(request):
    """Download filtered transactions as CSV."""
    qs = Transaction.objects.filter(user=request.user).select_related("category")

    month = request.GET.get("month")
    year = request.GET.get("year")
    txn_type = request.GET.get("type")

    if month and year:
        qs = qs.filter(date__month=int(month), date__year=int(year))
    if txn_type in ("INCOME", "EXPENSE"):
        qs = qs.filter(transaction_type=txn_type)

    now = timezone.now()
    filename = f'transactions_{now.strftime("%Y%m%d")}.csv'
    return export_csv(qs, filename)


@login_required
def export_pdf_view(request):
    """Download filtered transactions as PDF."""
    qs = Transaction.objects.filter(user=request.user).select_related("category")

    month = request.GET.get("month")
    year = request.GET.get("year")
    txn_type = request.GET.get("type")

    if month and year:
        qs = qs.filter(date__month=int(month), date__year=int(year))
        MONTH_NAMES = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        title = f"Expense Report — {MONTH_NAMES[int(month)]} {year}"
    else:
        title = "Expense Report — All Transactions"

    if txn_type in ("INCOME", "EXPENSE"):
        qs = qs.filter(transaction_type=txn_type)

    return export_pdf(qs, request.user, title)
