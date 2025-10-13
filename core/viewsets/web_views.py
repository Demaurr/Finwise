from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from core.models import Transaction
import json

def dashboard(request):
    return render(request, 'core/dashboard.html')


def add_transaction_page(request):
    return render(request, 'core/transactions.html')


def add_goal_page(request):
    return render(request, 'core/goals.html')
