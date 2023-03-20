from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.serializers import ValidationError, SerializerMethodField
from rest_framework.status import HTTP_400_BAD_REQUEST
from users.models import Follow
from re import match

User = get_user_model()


class RegisterUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id', 'email','username',
                  'first_name','last_name','password'
                )
        write_only_fields = ('password',)

    def validate_username(self, value):
        if not match(r'[\w.@+-]+', value):
            raise ValidationError('Неверный логин')
        return value


class ProcessUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                )
        
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class FollowSerializer(ProcessUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')
        
    def validate(self, data):
        user = self.context.get('request').user
        author = self.instance
        if user == author:
            raise ValidationError(
                detail='Пользователь не может подписаться сам на себя',
                code=HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            raise ValidationError(
                detail=('Пользователь не может повторно'
                        'подписаться на другого пользователя'),
                code=HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        from api.serializers import ShortRecipeSerializer
        recipes = obj.recipes.all()
        serializers = ShortRecipeSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializers.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

