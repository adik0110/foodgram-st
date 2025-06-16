from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    measurement_unit = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('recipes.Recipe', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.ingredient.name} – {self.amount} {self.ingredient.measurement_unit}"
