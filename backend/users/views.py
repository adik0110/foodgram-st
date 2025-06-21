from django.core.paginator import Paginator
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics, viewsets
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

from .models import Follow
from .serializers import (UserCreateSerializer,
                          UserSerializer,
                          AvatarSerializer,
                          SetPasswordSerializer,
                          SubscriptionUserSerializer)

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


class UserListCreateView(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPagination

    def get(self, request):
        users = User.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserCreateSerializer(user, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'


class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class UserAvatarUpdateDeleteView(APIView):
    def put(self, request):
        if 'avatar' not in request.data:
            return Response(
                {'avatar': ['Это поле обязательно.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': request.build_absolute_uri(request.user.avatar.url)}
        )

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if user == author:
            return Response(
                {'detail': 'Нельзя подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if user.follower.filter(following=author).exists():
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, following=author)
            serializer = SubscriptionUserSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            follow = user.follower.filter(following=author).first()
            if not follow:
                return Response(
                    {'detail': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        user = request.user
        # получаем queryset пользователей, на которых подписан юзер:
        following_qs = User.objects.filter(follower__user=user)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(following_qs, request)
        serializer = SubscriptionUserSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)
