from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Recipe
from .serializers import RecipeCreateSerializer, RecipeReadSerializer
from api.pagination import LimitPageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination  # опционально

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        # Тут можешь использовать более сложное создание ссылки, например через хеш
        short_code = f"s/{recipe.id}"  # простой вариант
        domain = "https://foodgram.example.org"
        short_link = f"{domain}/{short_code}"

        return Response({"short-link": short_link}, status=status.HTTP_200_OK)
