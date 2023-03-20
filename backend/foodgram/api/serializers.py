import base64

from users.serializers import ProcessUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.core.files.base import ContentFile
from rest_framework.serializers import (ModelSerializer,
                                        SerializerMethodField,
                                        ImageField,
                                        ValidationError,
                                        CharField
                                        )
from recipes.models import (Ingredient,
                            Tag,
                            Recipe,
                            RecipesTags,
                            IngredientsInRecipes,
                            Favorites,
                            Basket)
 


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientsWithAmount(ModelSerializer):
    measurement_unit = SerializerMethodField()

    class Meta:
        model = IngredientsInRecipes
        fields = '__all__'


    def get_measurement_unit(self, instance):
        return instance.ingredient.measurement_unit


class IngredientRecipeSerializer(ModelSerializer):
    id = CharField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')
    


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
    


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredientsinrecipes_set',
    )
    author = ProcessUserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_in_shopping_cart',
            'is_favorited',
        )

    def create(self, validated_data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipesTags.objects.create(tag_id=tag, recipe=recipe)
        for ingredient in ingredients:
            IngredientsInRecipes.objects.create(
                ingredient_id=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        tags = self.initial_data.get('tags')
        RecipesTags.objects.filter(recipe=instance).delete()
        for tag in tags:
            RecipesTags.objects.create(tag_id=tag, recipe=instance)
        ingredients = self.initial_data.get('ingredients')
        IngredientsInRecipes.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            IngredientsInRecipes.objects.create(
                ingredient_id=ingredient['id'],
                recipe=instance,
                amount=ingredient['amount']
            )
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorites.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()
    
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Basket.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()
    

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        if not ingredients:
            raise ValidationError(
                {'ingredients': ('В рецепте должен быть использован '
                                 'минимум один ингредиент')
                 }
            )
        array_of_ingredients = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, pk=ingredient['id']
            )
            if current_ingredient in array_of_ingredients:
                raise ValidationError(
                    detail='Ингредиенты не должны повторяться в рецепте',
                    code=HTTP_400_BAD_REQUEST
                )
            if int(ingredient['amount']) < 1:
                raise ValidationError(
                    {'ingredients': ('Количество ингредиента в рецепте '
                                     'должно быть больше или равно 1')
                     }
                )
        if not tags:
            raise ValidationError(
                {'tags': ('Рецепт должен быть привязан '
                          'как минимум к одному тегу')
                 }
            )
        array_of_tags = set(tags)
        if len(array_of_tags) != len(tags):
            raise ValidationError(
                detail='Теги не должны повторяться в рецепте',
                code=HTTP_400_BAD_REQUEST
            )
        return data