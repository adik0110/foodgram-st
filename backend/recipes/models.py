from django.contrib.auth import get_user_model
from django.db import models
from ingredients.models import Ingredient

User = get_user_model()

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='recipes/')
    description = models.TextField()
    cooking_time = models.PositiveIntegerField()  # в минутах

    ingredients = models.ManyToManyField(
        Ingredient,
        through='ingredients.RecipeIngredient',
        related_name='recipes'
    )

    def __str__(self):
        return self.name