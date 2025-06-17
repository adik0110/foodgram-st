from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    UserListCreateView,
    UserMeView,
    UserRetrieveView,
    UserAvatarUpdateDeleteView,
    SetPasswordView,
    UserViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('users/<int:id>/', UserRetrieveView.as_view(), name='user-detail'),
    path('users/me/avatar/',
         UserAvatarUpdateDeleteView.as_view(),
         name='user-avatar'),
    path('users/set_password/',
         SetPasswordView.as_view(),
         name='user-set-password'),
] + router.urls
