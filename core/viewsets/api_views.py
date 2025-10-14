from rest_framework import viewsets
from core.models import Transaction, FinancialGoal
from core.serializers import TransactionSerializer, FinancialGoalSerializer
from django.db.models import Sum
from core.models import Transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.processing.analytics import analyze_user_finances, full_user_analytics

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_data(request):
    user = request.user
    # data = analyze_user_finances(user)
    data = full_user_analytics(user)
    return Response(data)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FinancialGoalViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialGoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FinancialGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-date')[:10]

    total_income = Transaction.objects.filter(user=user, type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Transaction.objects.filter(user=user, type='expense').aggregate(total=Sum('amount'))['total'] or 0
    savings_rate = 0 if total_income == 0 else round((total_income - total_expense) / total_income * 100, 2)

    data = {
        "total_income": total_income,
        "total_expense": total_expense,
        "savings_rate": savings_rate,
        "transactions": [
            {
                "date": tx.date.strftime('%Y-%m-%d'),
                "category": tx.category,
                "amount": float(tx.amount),
                "description": tx.notes or ""
            }
            for tx in transactions
        ]
    }
    return Response(data)