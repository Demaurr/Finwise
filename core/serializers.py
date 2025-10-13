from rest_framework import serializers
from .models import Transaction, FinancialGoal

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user', 'date']


class FinancialGoalSerializer(serializers.ModelSerializer):
    progress = serializers.ReadOnlyField()

    class Meta:
        model = FinancialGoal
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'progress']
