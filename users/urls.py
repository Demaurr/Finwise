from django.urls import path
from .views import register_page, login_page, logout_view

from django.urls import path

urlpatterns = [
    path('register/', register_page, name='register_page'),
    path('login/', login_page, name='login_page'),
    path('logout/', logout_view, name='logout_page'),
]
