from django.contrib.auth import get_user_model
from django.db import models
from ingredients.models import Ingredient

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    shopping_cart = models.ManyToManyField(
        User,
        related_name='cart_recipes',
        blank=True
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='ingredients.RecipeIngredient',
        related_name='recipes'
    )

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
