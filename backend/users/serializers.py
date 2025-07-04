from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.password_validation import validate_password
from drf_extra_fields.fields import Base64ImageField
import re


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True, 'max_length': 150},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                "Может содержать только буквы, цифры и символы @ . + - _"
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль.")
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class SubscriptionUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()

    def get_recipes(self, obj):
        from recipes.serializers import RecipeShortSerializer
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes_qs = obj.recipes.all()
        if recipes_limit:
            try:
                limit = int(recipes_limit)
                recipes_qs = recipes_qs[:limit]
            except ValueError:
                pass
        serializer = RecipeShortSerializer(
            recipes_qs,
            many=True,
            context=self.context
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
