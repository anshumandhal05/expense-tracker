"""Budgets views — CRUD with live spending status."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BudgetForm
from .models import Budget


@login_required
def budget_list(request):
    """Show all budgets for the current user with live spend data."""
    now = timezone.now()
    budgets = Budget.objects.filter(user=request.user).select_related("category")

    # Annotate each budget with real-time spend info
    budget_data = []
    for budget in budgets:
        spent = budget.get_spent()
        remaining = budget.get_remaining()
        percentage = budget.get_percentage()
        exceeded = budget.is_exceeded()
        budget_data.append(
            {
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "percentage": percentage,
                "exceeded": exceeded,
            }
        )

    alert_count = sum(1 for b in budget_data if b["exceeded"])

    return render(
        request,
        "budgets/budget_list.html",
        {
            "budget_data": budget_data,
            "alert_count": alert_count,
            "current_month": now.month,
            "current_year": now.year,
        },
    )


@login_required
def budget_add(request):
    """Add a new budget limit."""
    if request.method == "POST":
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, f'Budget for {budget.category or "Overall"} set to ₹{budget.monthly_limit}!')
            return redirect("budget_list")
        else:
            messages.error(request, "Please fix the errors.")
    else:
        form = BudgetForm(user=request.user)
    return render(request, "budgets/budget_form.html", {"form": form, "action": "Set"})


@login_required
def budget_edit(request, pk):
    """Edit an existing budget."""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Budget updated!")
            return redirect("budget_list")
    else:
        form = BudgetForm(instance=budget, user=request.user)
    return render(request, "budgets/budget_form.html", {"form": form, "action": "Edit", "budget": budget})


@login_required
def budget_delete(request, pk):
    """Delete a budget."""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == "POST":
        budget.delete()
        messages.success(request, "Budget removed.")
        return redirect("budget_list")
    return render(request, "budgets/budget_confirm_delete.html", {"budget": budget})
