# from django.contrib import admin
# from .models import Recipe
# from favorites.models import Favorite  # если избранное — отдельная модель
#
# @admin.register(Recipe)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'author', 'favorites_count')
#     search_fields = ('name', 'author__username', 'author__email')
#     readonly_fields = ('favorites_count',)
#
#     def favorites_count(self, obj):
#         return Favorite.objects.filter(recipe=obj).count()
#     favorites_count.short_description = 'Добавлений в избранное'
