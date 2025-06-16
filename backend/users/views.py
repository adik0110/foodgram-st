from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer, UserListSerializer

User = get_user_model()

class UserListCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        users = User.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'limit'  # можно передавать limit в query params
        page = paginator.paginate_queryset(users, request)
        serializer = UserListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserListSerializer(user, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
