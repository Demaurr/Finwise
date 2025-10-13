from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Transaction
import json
from django.db.models import Sum
from .models import Transaction, FinancialGoal
from rest_framework import viewsets, permissions
from .serializers import TransactionSerializer, FinancialGoalSerializer

@login_required(login_url="/users/login/")
def dashboard(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    
    categories = transactions.values_list('category', flat=True).distinct()
    data = []
    for cat in categories:
        total = transactions.filter(category=cat).aggregate(total=Sum('amount'))['total'] or 0
        data.append({'category': cat, 'total': total})
    
    chart_data = {
        'labels': [d['category'] for d in data],
        'datasets': [{
            'label': 'Monthly Overview',
            'data': [float(d['total']) for d in data],
            'backgroundColor': [
                'rgba(75, 192, 192, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(255, 99, 132, 0.5)',
                'rgba(153, 102, 255, 0.5)'
            ]
        }]
    }

    context = {
        'chart_data': json.dumps(chart_data),
        'transactions': transactions.order_by('-date')[:5]
    }
    return render(request, 'core/dashboard.html', context)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FinancialGoalViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FinancialGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@login_required(login_url="/users/login/")
def add_transaction_page(request):
    return render(request, 'core/add_transaction.html')

@login_required(login_url="/users/login/")
def add_goal_page(request):
    return render(request, 'core/add_goal.html')