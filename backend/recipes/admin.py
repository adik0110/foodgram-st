from django.contrib import admin
from .models import Recipe, Favorite

class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__email', 'author__username')
    list_filter = ('name', 'author')
    inlines = (RecipeIngredientInline,)
    exclude = ('ingredients',)
    empty_value_display = '-пусто-'

    def favorites_count(self, obj):
        return obj.favorites.count()
    favorites_count.short_description = 'В избранном'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__email', 'recipe__name')
    empty_value_display = '-пусто-'