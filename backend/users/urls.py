from django.urls import path
from .views import UserListCreateView, UserMeView, UserRetrieveView

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/me/', UserMeView.as_view(), name='user-me'),                # GET текущий юзер
    path('users/<int:id>/', UserRetrieveView.as_view(), name='user-detail'),# GET по id
]
