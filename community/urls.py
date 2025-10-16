from django.urls import path, include
from .views import community_page

urlpatterns = [
    path("community/posts/", community_page, name="community-page")
]