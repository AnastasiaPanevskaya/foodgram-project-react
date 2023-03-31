from django.contrib import admin
from django.contrib.admin import ModelAdmin
from recipes.models import (Basket, Favorites, Ingredient, Recipe,
                            RecipeIngredient, Tag)


class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags')

    def count_favorites(self, obj):
        return obj.favorites.count()


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorites)
admin.site.register(Basket)
admin.site.register(RecipeIngredient)
