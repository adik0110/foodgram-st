from collections import defaultdict

from django.db.models import F, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination

from .filters import RecipeFilter
from .models import Recipe
from .serializers import RecipeCreateSerializer, RecipeReadSerializer, RecipeShortSerializer
from .permissions import IsAuthorOrReadOnly
from ingredients.models import RecipeIngredient


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user

        is_in_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_cart in ['1', 'true', 'True'] and user.is_authenticated:
            queryset = queryset.filter(shopping_cart=user)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in ['1', 'true', 'True'] and user.is_authenticated:
            queryset = queryset.filter(favorites__user=user)

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Необходимо авторизоваться для создания рецепта.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        read_serializer = RecipeReadSerializer(
            recipe, context={'request': request}
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_code = f"s/{recipe.id}"
        short_link = request.build_absolute_uri(f"/{short_code}")
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='shopping_cart'
    )
    def add_to_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        if recipe.shopping_cart.filter(id=user.id).exists():
            return Response(
                {"detail": "Рецепт уже в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe.shopping_cart.add(user)
        serializer = RecipeShortSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        user = request.user
        try:
            recipe = self.get_object()
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Рецепт не найден."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not recipe.shopping_cart.filter(id=user.id).exists():
            return Response(
                {"detail": "Рецепт не в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe.shopping_cart.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart=user
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('name')

        lines = ['Список покупок:\n']
        for item in ingredients:
            line = f"{item['name']} ({item['unit']}) — {item['total_amount']}\n"
            lines.append(line)

        content = ''.join(lines)

        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
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
            serializer = RecipeShortSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = recipe.favorites.filter(user=user).first()
            if not favorite:
                return Response(
                    {"detail": "Рецепта нет в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)