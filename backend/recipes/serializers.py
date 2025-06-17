from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from ingredients.models import Ingredient, RecipeIngredient
from users.serializers import UserSerializer
from .models import Recipe


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
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один ингредиент."
            )

        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться."
            )

        existing_ids = set(
            Ingredient.objects.filter(id__in=ids).values_list('id', flat=True)
        )
        invalid_ids = set(ids) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"Некорректные ингредиенты: {', '.join(map(str, invalid_ids))}"
            )

        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                "Поле image не может быть пустым."
            )
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть не меньше 1 минуты."
            )
        return value

    def validate(self, data):
        request_method = self.context['request'].method
        if request_method in ['PUT', 'PATCH'] and 'ingredients' not in data:
            raise serializers.ValidationError({
                'ingredients': 'Поле ingredients обязательно при обновлении.'
            })
        return data

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
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients is not None:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.create_ingredients(instance, ingredients)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
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
        serializer = IngredientReadSerializer(
            obj.ingredients.all(),
            many=True,
            context={'recipe': obj}
        )
        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and obj.favorites.filter(user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and obj.shopping_cart.filter(id=user.id).exists())


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
