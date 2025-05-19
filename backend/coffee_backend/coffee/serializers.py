from rest_framework import serializers
from .models.user import User
from .models.coffee import Coffee, Origin
from .models.uploads import UploadedFile
from .models.operations import Operation
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth import authenticate
from .models.user_profile import UserProfile

class OriginSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Origin
        fields = ['id', 'name']

class CoffeeSerializer(serializers.ModelSerializer):
    origin = OriginSerializer()
    user   = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model  = Coffee
        fields = ['id', 'name', 'origin', 'description', 'user']

    def create(self, validated_data):
        origin_data = validated_data.pop('origin')
        origin, _ = Origin.objects.get_or_create(**origin_data)
        user = self.context['request'].user
        return Coffee.objects.create(origin=origin, user=user, **validated_data)

    def update(self, instance, validated_data):
        origin_data = validated_data.pop('origin', None)
        if origin_data:
            origin, _ = Origin.objects.get_or_create(**origin_data)
            instance.origin = origin
        instance.name        = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UploadedFile
        fields = ['id', 'file', 'uploaded_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model  = AuthUser
        fields = ('username', 'email', 'password')

    def validate_username(self, value):
        if value.lower() == 'admin':
            raise serializers.ValidationError("Username 'admin' is reserved.")
        return value

    def create(self, validated_data):
        user = AuthUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get('username'),
            password=data.get('password'),
        )
        if user and user.is_active:
            return {'user': user}
        raise serializers.ValidationError("Invalid credentials.")

class UserSerializer(serializers.ModelSerializer):
    operations = serializers.SerializerMethodField()

    class Meta:
        model  = AuthUser
        fields = ['id', 'username', 'email', 'last_login', 'date_joined', 'operations']

    def get_operations(self, obj):
        ops = Operation.objects.filter(user_id=obj.id).order_by('timestamp')
        return [
            {
                'operation': op.operation,
                'timestamp': op.timestamp.isoformat()
            }
            for op in ops
        ]

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'email', 'last_login', 'date_joined']

class OperationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Operation
        fields = ['id', 'user', 'username', 'operation', 'timestamp']



# coffee/serializers.py

# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models.coffee import Coffee, Origin
# from .models.uploads import UploadedFile
#
# # Use the default User model (table auth_user)
# User = get_user_model()
#
#
# class OriginSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Origin
#         fields = ['id', 'name']
#
#
# class CoffeeSerializer(serializers.ModelSerializer):
#     origin = OriginSerializer()
#     user   = serializers.PrimaryKeyRelatedField(read_only=True)
#
#     class Meta:
#         model  = Coffee
#         fields = ['id', 'name', 'origin', 'description', 'user']
#
#     def create(self, validated_data):
#         origin_data = validated_data.pop('origin')
#         if not origin_data or 'name' not in origin_data:
#             raise serializers.ValidationError("Origin data is missing or invalid.")
#         origin, _ = Origin.objects.get_or_create(**origin_data)
#         user = self.context['request'].user
#         return Coffee.objects.create(origin=origin, user=user, **validated_data)
#
#     def update(self, instance, validated_data):
#         origin_data = validated_data.pop('origin', None)
#         if origin_data:
#             origin, _ = Origin.objects.get_or_create(**origin_data)
#             instance.origin = origin
#         instance.name        = validated_data.get('name', instance.name)
#         instance.description = validated_data.get('description', instance.description)
#         instance.save()
#         return instance
#
#
# class UploadedFileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = UploadedFile
#         fields = ['id', 'file', 'uploaded_at']
#
#
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#
#     class Meta:
#         model  = User
#         fields = ('username', 'email', 'password')
#
#     def validate_username(self, value):
#         if value.lower() == 'admin':
#             raise serializers.ValidationError("Username 'admin' is reserved.")
#         return value
#
#     def create(self, validated_data):
#         # Store password as plain text (INSECURE)
#         return User.objects.create(
#             username=validated_data['username'],
#             email=validated_data.get('email'),
#             password=validated_data['password'],
#         )
#
#
# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)
#
#     def validate(self, data):
#         from django.contrib.auth import authenticate
#         user = authenticate(
#             username=data.get('username'),
#             password=data.get('password'),
#         )
#         if user and user.is_active:
#             return {'user': user}
#         raise serializers.ValidationError("Invalid credentials.")
#
#
# class UserSerializer(serializers.ModelSerializer):
#     operations = serializers.CharField(required=False, allow_blank=True)
#
#     class Meta:
#         model  = User
#         fields = ['id', 'username', 'email', 'operations']
