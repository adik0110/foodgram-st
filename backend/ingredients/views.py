from rest_framework import viewsets, filters, permissions
from ingredients.models import Ingredient
from .serializers import IngredientSerializer


class IngredientNameFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        name_param = request.query_params.get('name')
        if name_param:
            return queryset.filter(name__istartswith=name_param)
        return queryset


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientNameFilter]
    permission_classes = [permissions.AllowAny]
    pagination_class = None
