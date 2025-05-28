from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password2', 'phone_number', 'address')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'phone_number', 'address', 'twofa', 'twofa_email', 'is_special_admin')
        read_only_fields = ('id',)

class AdminUserSerializer(serializers.ModelSerializer):
    is_2fa_enabled = serializers.SerializerMethodField()
    operations = serializers.SerializerMethodField()
    is_suspicious = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                 'address', 'twofa', 'twofa_email', 'is_special_admin', 'is_2fa_enabled',
                 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
                 'operations', 'is_suspicious')
        read_only_fields = ('id',)
    
    def get_is_2fa_enabled(self, obj):
        return obj.twofa
    
    def get_operations(self, obj):
        try:
            operations = obj.coffee_operations.all()[:10]  # Last 10 operations
            return CoffeeOperationSerializer(operations, many=True).data
        except:
            return []
    
    def get_is_suspicious(self, obj):
        """Check if user has more than 5 consecutive deletes"""
        try:
            recent_operations = obj.coffee_operations.all()[:10]  # Check last 10 operations
            consecutive_deletes = 0
            max_consecutive_deletes = 0
            
            for operation in recent_operations:
                if operation.operation_type == 'delete':
                    consecutive_deletes += 1
                    max_consecutive_deletes = max(max_consecutive_deletes, consecutive_deletes)
                else:
                    consecutive_deletes = 0
            
            return max_consecutive_deletes > 5
        except:
            return False

class TwoFactorSetupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class TwoFactorVerifySerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)
    code = serializers.CharField(required=False, min_length=6, max_length=6)
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        
        if not username and not email:
            raise serializers.ValidationError("Either username or email is required")
        
        # Use email if provided, otherwise use username
        attrs['login_field'] = email if email else username
        return attrs 

class CoffeeOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = None  # Will be set after import
        fields = ('operation_type', 'coffee_id', 'coffee_name', 'timestamp')

# Import after to avoid circular imports
try:
    from coffee.models.coffee_operations import CoffeeOperation
    CoffeeOperationSerializer.Meta.model = CoffeeOperation
except ImportError:
    pass 