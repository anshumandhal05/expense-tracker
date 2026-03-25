"""Accounts views — register, login, logout, profile."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.shortcuts import redirect, render

from .forms import UserRegistrationForm


def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}! Your account has been created.")
            return redirect("dashboard")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get("next", "dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """User logout."""
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been logged out successfully.")
        return redirect("login")
    return redirect("dashboard")


@login_required
def profile_view(request):
    """User profile with financial summary."""
    from django.utils import timezone

    from budgets.models import Budget
    from expenses.models import Transaction

    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # All-time totals
    total_income = (
        Transaction.objects.filter(user=request.user, transaction_type="INCOME").aggregate(total=Sum("amount"))[
            "total"
        ]
        or 0
    )

    total_expense = (
        Transaction.objects.filter(user=request.user, transaction_type="EXPENSE").aggregate(total=Sum("amount"))[
            "total"
        ]
        or 0
    )

    balance = total_income - total_expense

    # Monthly totals
    monthly_income = (
        Transaction.objects.filter(
            user=request.user, transaction_type="INCOME", date__month=current_month, date__year=current_year
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    monthly_expense = (
        Transaction.objects.filter(
            user=request.user, transaction_type="EXPENSE", date__month=current_month, date__year=current_year
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    # Transaction count
    transaction_count = Transaction.objects.filter(user=request.user).count()
    budget_count = Budget.objects.filter(user=request.user).count()

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        "transaction_count": transaction_count,
        "budget_count": budget_count,
    }
    return render(request, "accounts/profile.html", context)
