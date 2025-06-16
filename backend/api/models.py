from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('г', 'грамм'),
        ('мл', 'миллилитр'),
        ('шт', 'штука'),
        ('чл', 'чайная ложка'),
        ('сл', 'столовая ложка'),
        ('щеп', 'щепотка'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Название продукта")
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        verbose_name="Единица измерения"
    )

    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор публикации"
    )
    title = models.CharField(max_length=200, verbose_name="Название рецепта")
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name="Картинка рецепта"
    )
    description = models.TextField(verbose_name="Текстовое описание")
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления (в минутах)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ['-created_at']


class RecipeIngredient(models.Model):
    """Связь рецепта и ингредиентов с количеством"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return f"{self.amount} {self.ingredient.unit} {self.ingredient.name}"

    class Meta:
        unique_together = ('recipe', 'ingredient')