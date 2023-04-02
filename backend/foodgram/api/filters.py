from django.contrib.auth import get_user_model
from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (
    ModelChoiceFilter,
    BooleanFilter,
    AllValuesMultipleFilter,
    CharFilter
)
from recipes.models import Ingredient, Recipe

User = get_user_model()


class IngredientFilter(FilterSet):
    name = CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):

        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            startswith=ExpressionWrapper(
                Q(name__istartswith=value),
                output_field=BooleanField()
            )
        ).order_by('-startswith')


class RecipeFilter(FilterSet):
    author = ModelChoiceFilter(queryset=User.objects.all())
    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
        # to_field_name='slug',
        # queryset=Tag.objects.all(),
        lookup_expr='Ссылка'
    )
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(basket__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)
