from rest_framework import serializers
from .models.user import User
from .models.coffee import Coffee, Origin, Like, ConsumedCoffee
from .models.uploads import UploadedFile
from .models.operations import Operation
from .models.challenges import Challenge, ChallengeRecipe, Vote, Notification
from .models.health import UserHealthProfile, BloodPressureEntry
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth import authenticate
from .models.user_profile import UserProfile
from users.serializers import UserSerializer as CustomUserSerializer

class OriginSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Origin
        fields = ['id', 'name']

class CoffeeSerializer(serializers.ModelSerializer):
    origin = OriginSerializer()
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    caffeine_mg = serializers.SerializerMethodField()

    class Meta:
        model  = Coffee
        fields = ['id', 'name', 'origin', 'description', 'user', 'likes_count', 'is_liked', 'is_community_winner', 'caffeine_mg']

    def get_caffeine_mg(self, obj):
        """Get caffeine content using the model's method"""
        try:
            return obj.get_caffeine_mg()
        except (AttributeError, TypeError):
            # Fallback if method doesn't exist or returns None
            return getattr(obj, 'caffeine_mg', 95.0) or 95.0

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

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
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid username or password')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        data['user'] = user
        return data

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

# Challenge System Serializers
class ChallengeRecipeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    origin = OriginSerializer()

    class Meta:
        model = ChallengeRecipe
        fields = ['id', 'user', 'name', 'origin', 'description', 'created_at']

    def create(self, validated_data):
        origin_data = validated_data.pop('origin')
        origin, _ = Origin.objects.get_or_create(**origin_data)
        return ChallengeRecipe.objects.create(origin=origin, **validated_data)

class ChallengeSerializer(serializers.ModelSerializer):
    challenger = CustomUserSerializer(read_only=True)
    challenged = CustomUserSerializer(read_only=True)
    winner = CustomUserSerializer(read_only=True)
    recipes = ChallengeRecipeSerializer(many=True, read_only=True)
    total_votes = serializers.ReadOnlyField()
    challenger_votes = serializers.ReadOnlyField()
    challenged_votes = serializers.ReadOnlyField()
    can_vote = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            'id', 'challenger', 'challenged', 'coffee_type', 'status', 
            'created_at', 'accepted_at', 'completed_at', 'winner',
            'recipes', 'total_votes', 'challenger_votes', 'challenged_votes',
            'can_vote', 'user_vote'
        ]

    def get_can_vote(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        # Can't vote if you're a participant or if not in voting phase
        if obj.status != 'voting':
            return False
        if user == obj.challenger or user == obj.challenged:
            return False
        # Can't vote if already voted
        if obj.votes.filter(voter=user).exists():
            return False
        return True

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        vote = obj.votes.filter(voter=request.user).first()
        return vote.voted_for.username if vote else None

class VoteSerializer(serializers.ModelSerializer):
    voter = CustomUserSerializer(read_only=True)
    voted_for = CustomUserSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ['id', 'voter', 'voted_for', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'message', 'challenge', 'is_read', 'created_at']


# Health and Consumption Serializers
class ConsumedCoffeeSerializer(serializers.ModelSerializer):
    coffee = CoffeeSerializer(read_only=True)
    coffee_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = ConsumedCoffee
        fields = ['id', 'coffee', 'coffee_id', 'consumed_at']
        read_only_fields = ['consumed_at']


class BloodPressureEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodPressureEntry
        fields = ['id', 'systolic', 'diastolic', 'pulse', 'measured_at', 'notes']
        read_only_fields = ['measured_at']


class UserHealthProfileSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    bmi = serializers.ReadOnlyField()

    class Meta:
        model = UserHealthProfile
        fields = [
            'id', 'sex', 'date_of_birth', 'age', 'height_cm', 'weight_kg', 'bmi',
            'has_family_history_chd', 'num_relatives_chd', 'family_history_details',
            'has_hypertension', 'has_diabetes', 'has_high_cholesterol', 'has_obesity',
            'is_smoker', 'activity_level', 'other_health_issues',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']



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
