from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

class User(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(),),
        help_text='Придумайте логин'
    )
    email = models.EmailField(
        'Почта',
        max_length=254,
        help_text='Укажите электронную почту'
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        help_text='Укажите имя'
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        help_text='Укажите фамилию'
    )
    password = models.CharField(
        'Пароль',
        max_length=150
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
    

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user_cannot_follow_himself'
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            )
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    
    def __str__(self):
        return f'{self.user} подписался на {self.author}'
