# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
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
                "Имя пользователя может содержать только буквы, цифры и символы @ . + - _"
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


# users/serializers.py
class UserListSerializer(serializers.ModelSerializer):
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


# users/serializers.py
class UserDetailSerializer(serializers.ModelSerializer):
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
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


# users/serializers.py
class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
