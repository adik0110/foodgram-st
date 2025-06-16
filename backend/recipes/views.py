from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

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
