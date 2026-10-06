from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm


def expense_list(request):
    expenses = Expense.objects.all()

    # Filter by category if chosen
    selected_category = request.GET.get('category', '')
    if selected_category:
        expenses = expenses.filter(category=selected_category)

    # Total of what is currently shown
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Total per category (always for all expenses)
    category_totals = (
        Expense.objects.values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    context = {
        'expenses': expenses,
        'total': total,
        'category_totals': category_totals,
        'categories': [c[0] for c in Expense.CATEGORY_CHOICES],
        'selected_category': selected_category,
    }
    return render(request, 'expenses/expense_list.html', context)


def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form, 'heading': 'Add Expense'})


def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'heading': 'Edit Expense'})


def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})