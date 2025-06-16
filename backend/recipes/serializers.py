from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from .models import Recipe
from ingredients.models import Ingredient, RecipeIngredient
from users.serializers import UserDetailSerializer


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientReadSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        recipe = self.context.get('recipe')
        if recipe is None:
            return None
        recipe_ingredient = RecipeIngredient.objects.filter(
            recipe=recipe,
            ingredient=obj
        ).first()
        return recipe_ingredient.amount if recipe_ingredient else None


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()
    name = serializers.CharField(max_length=256)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'image', 'name', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо указать хотя бы один ингредиент.")
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Ингредиенты не должны повторяться.")
        return value

    def create_ingredients(self, recipe, ingredients_data):
        bulk = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=item['id']),
                amount=item['amount']
            )
            for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(bulk)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user, **validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        # Передаем в контекст текущий рецепт (obj)
        serializer = IngredientReadSerializer(
            obj.ingredients.all(),
            many=True,
            context={'recipe': obj}
        )
        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.shopping_cart.filter(id=user.id).exists()