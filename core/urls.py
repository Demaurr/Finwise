from django.urls import path
from core.viewsets import web_views

urlpatterns = [
    path('', web_views.dashboard, name='dashboard'),
    path('add-transaction/', web_views.add_transaction_page, name='add_transaction_page'),
    path('add-goal/', web_views.add_goal_page, name='add_goal_page'),
]
