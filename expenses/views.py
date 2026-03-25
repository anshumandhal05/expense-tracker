"""Expenses views — CRUD for transactions and categories."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm, TransactionFilterForm, TransactionForm
from .models import Category, Transaction

# ─── Transaction Views ──────────────────────────────────────────────────────


@login_required
def transaction_list(request):
    """Paginated, filterable transaction list."""
    qs = Transaction.objects.filter(user=request.user).select_related("category")
    form = TransactionFilterForm(request.GET or None, user=request.user)

    if form.is_valid():
        q = form.cleaned_data.get("query")
        t_type = form.cleaned_data.get("transaction_type")
        cat = form.cleaned_data.get("category")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")

        if q:
            qs = qs.filter(Q(description__icontains=q) | Q(notes__icontains=q))
        if t_type:
            qs = qs.filter(transaction_type=t_type)
        if cat:
            qs = qs.filter(category=cat)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "expenses/transaction_list.html",
        {
            "page_obj": page_obj,
            "filter_form": form,
            "total_count": qs.count(),
        },
    )


@login_required
def transaction_add(request):
    """Add a new transaction."""
    initial = {}
    t_type = request.GET.get("type", "EXPENSE")
    if t_type in ("INCOME", "EXPENSE"):
        initial["transaction_type"] = t_type

    if request.method == "POST":
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            txn = form.save(commit=False)
            txn.user = request.user
            txn.save()
            messages.success(request, f"{txn.get_transaction_type_display()} of ₹{txn.amount} added successfully!")
            return redirect("transaction_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = TransactionForm(user=request.user, initial=initial)

    return render(
        request,
        "expenses/transaction_form.html",
        {
            "form": form,
            "action": "Add",
        },
    )


@login_required
def transaction_edit(request, pk):
    """Edit an existing transaction."""
    txn = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=txn, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully!")
            return redirect("transaction_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = TransactionForm(instance=txn, user=request.user)

    return render(
        request,
        "expenses/transaction_form.html",
        {
            "form": form,
            "action": "Edit",
            "txn": txn,
        },
    )


@login_required
def transaction_delete(request, pk):
    """Delete a transaction (POST only)."""
    txn = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        txn.delete()
        messages.success(request, "Transaction deleted.")
        return redirect("transaction_list")
    return render(request, "expenses/transaction_confirm_delete.html", {"txn": txn})


# ─── Category Views ──────────────────────────────────────────────────────────


@login_required
def category_list(request):
    """List user categories + system defaults."""
    user_cats = Category.objects.filter(user=request.user)
    system_cats = Category.objects.filter(user=None)
    return render(
        request,
        "expenses/category_list.html",
        {
            "user_cats": user_cats,
            "system_cats": system_cats,
        },
    )


@login_required
def category_add(request):
    """Add a custom category."""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request, f'Category "{cat.name}" created!')
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(request, "expenses/category_form.html", {"form": form, "action": "Add"})


@login_required
def category_edit(request, pk):
    """Edit a user-owned category."""
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated!")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=cat)
    return render(request, "expenses/category_form.html", {"form": form, "action": "Edit", "cat": cat})


@login_required
def category_delete(request, pk):
    """Delete a user-owned category."""
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == "POST":
        cat.delete()
        messages.success(request, f'Category "{cat.name}" deleted.')
        return redirect("category_list")
    return render(request, "expenses/category_confirm_delete.html", {"cat": cat})
