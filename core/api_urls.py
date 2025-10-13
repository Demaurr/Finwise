from rest_framework.routers import DefaultRouter
from core.viewsets.api_views import TransactionViewSet, FinancialGoalViewSet, dashboard_data
from django.urls import path, include

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'goals', FinancialGoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-data/', dashboard_data, name='dashboard-data'),
]
