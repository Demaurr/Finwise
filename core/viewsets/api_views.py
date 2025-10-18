from rest_framework import viewsets
from core.models import Transaction, FinancialGoal
from core.serializers import TransactionSerializer, FinancialGoalSerializer
from django.db.models import Sum
from core.models import Transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.utils.analytics import analyze_user_finances, full_user_analytics


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
    
    analytics = full_user_analytics(user)

    transactions = Transaction.objects.filter(user=user).order_by('-date')[:10]
    total_income = analytics['personal']['total_income']
    total_expense = analytics['personal']['total_expense']
    savings_rate = analytics['personal']['savings_rate']
    insights = analytics['insights']

    comparison = analytics.get('comparison', {})
    region_savings_rate = comparison.get('region_savings_rate')
    print(region_savings_rate)

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
        ],
        "insights": insights,
        "comparison": {
            "region_avg_income": comparison.get("region_avg_income"),
            "region_avg_expense": comparison.get("region_avg_expense"),
            "region_savings_rate": region_savings_rate,
            "region": comparison.get("region"),
        }
    }
    return Response(data)
