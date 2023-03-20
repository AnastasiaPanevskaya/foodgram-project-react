from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    name = models.CharField('Название', unique=True, max_length=200)
    color = models.CharField('Цвет', unique=True, max_length=16,)
    slug = models.SlugField('Уникальный слаг', unique=True)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название',
        help_text='Укажите наименование рецепта'
    )
    text = models.TextField(
        max_length=256,
        help_text='Укажите описание рецепта')
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipesTags',
        verbose_name='Тег'
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='recipes/',
        help_text='Добавьте картинку')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1, message='Установите минимальное значение')]

    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipes',
        verbose_name='Ингредиенты',
        help_text='Добавьте ингредиенты для рецепта'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsInRecipes(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1, message='Установите минимальное количество!')]
    )

    class Meta:
        verbose_name = 'Связь ингредиентов и рецептов'
        verbose_name_plural = 'Связь ингредиентов и рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='Связь ингредиента и рецепта должна быть уникальна'
            )
        ]
    

class RecipesTags(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Связь тегов и рецептов'
        verbose_name_plural = 'Связь тегов и рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='Связь между тегом и рецептом должна быть уникальна'
            )
        ]
    

class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Пользователь не может добавить рецепт в Избранное дважды'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в Избранное рецепт {self.recipe}'
    

class Basket(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='baskets'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='baskets'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Пользователь не может добавить рецепт в Корзину дважды'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в Корзину рецепт {self.recipe}'
