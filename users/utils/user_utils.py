from .ip_utils import get_client_ip, get_ip_location
from core.models import Transaction
from django.db.models import Sum


def update_user_location_if_missing(request, user):
    """If user has no location, update it using their IP."""
    if not user.location:
        ip = get_client_ip(request)
        location_data = get_ip_location(ip)
        if location_data:
            user.location = location_data
            user.save(update_fields=["location"])

def calculate_user_savings(user):
    transactions = Transaction.objects.filter(user=user)
    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_savings = total_income - total_expense
    savings_rate = round((net_savings / total_income) * 100, 2) if total_income > 0 else 0
    return savings_rate
