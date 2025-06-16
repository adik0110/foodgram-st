from collections import defaultdict

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Recipe
from .serializers import RecipeCreateSerializer, RecipeReadSerializer
from api.pagination import LimitPageNumberPagination
from .permissions import IsAuthorOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination  # опционально

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        # Тут можешь использовать более сложное создание ссылки, например через хеш
        short_code = f"s/{recipe.id}"  # простой вариант
        domain = "https://foodgram.example.org"
        short_link = f"{domain}/{short_code}"

        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='shopping_cart')
    def add_to_shopping_cart(self, request, pk=None):
        user = request.user
        try:
            recipe = self.get_object()
        except Recipe.DoesNotExist:
            return Response({"detail": "Рецепт не найден."}, status=status.HTTP_404_NOT_FOUND)

        if recipe.shopping_cart.filter(id=user.id).exists():
            return Response({"detail": "Рецепт уже в списке покупок."}, status=status.HTTP_400_BAD_REQUEST)

        recipe.shopping_cart.add(user)
        serializer_data = {
            "id": recipe.id,
            "name": recipe.name,
            "image": request.build_absolute_uri(recipe.image.url),
            "cooking_time": recipe.cooking_time
        }
        return Response(serializer_data, status=status.HTTP_201_CREATED)

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        user = request.user
        try:
            recipe = self.get_object()
        except Recipe.DoesNotExist:
            return Response({"detail": "Рецепт не найден."}, status=status.HTTP_404_NOT_FOUND)

        if not recipe.shopping_cart.filter(id=user.id).exists():
            return Response({"detail": "Рецепт не в списке покупок."}, status=status.HTTP_400_BAD_REQUEST)

        recipe.shopping_cart.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated],
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        # Получаем все рецепты в списке покупок пользователя
        recipes = user.cart_recipes.prefetch_related('ingredients', 'ingredients__recipes')

        # Собираем суммарное количество каждого ингредиента
        ingredients_count = defaultdict(lambda: {'name': '', 'measurement_unit': '', 'amount': 0})

        for recipe in recipes:
            for ri in recipe.recipeingredient_set.all():
                ingredient = ri.ingredient
                data = ingredients_count[ingredient.id]
                data['name'] = ingredient.name
                data['measurement_unit'] = ingredient.measurement_unit
                data['amount'] += ri.amount

        # Формируем содержимое файла (txt)
        lines = ['Список покупок:\n']
        for ing in ingredients_count.values():
            line = f"{ing['name']} - {ing['amount']} {ing['measurement_unit']}\n"
            lines.append(line)

        content = ''.join(lines)

        response = HttpResponse(content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if recipe.favorites.filter(user=user).exists():
                return Response(
                    {"detail": "Рецепт уже в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe.favorites.create(user=user)
            data = {
                "id": recipe.id,
                "name": recipe.name,
                "image": request.build_absolute_uri(recipe.image.url),
                "cooking_time": recipe.cooking_time,
            }
            return Response(data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = recipe.favorites.filter(user=user).first()
            if not favorite:
                return Response(
                    {"detail": "Рецепта нет в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)