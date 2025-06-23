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
        extra_kwargs = {
            'email': {'validators': []},  # Remove unique validation for email
            'username': {'validators': []},  # Remove unique validation for username
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Check if user exists and is banned - allow re-registration
        username = attrs.get('username')
        email = attrs.get('email')
        
        try:
            existing_user = User.objects.get(username=username)
            if existing_user.is_banned:
                # Allow re-registration for banned users
                attrs['_reregistering_banned_user'] = existing_user
            elif existing_user:
                # User exists and is not banned - prevent registration
                raise serializers.ValidationError({"username": "A user with that username already exists."})
        except User.DoesNotExist:
            pass  # User doesn't exist, proceed normally
        
        # Check email uniqueness too
        try:
            existing_user_email = User.objects.get(email=email)
            if existing_user_email.is_banned:
                # Allow re-registration for banned users with same email
                if not attrs.get('_reregistering_banned_user'):
                    attrs['_reregistering_banned_user'] = existing_user_email
            elif existing_user_email:
                # User exists and is not banned - prevent registration
                raise serializers.ValidationError({"email": "A user with that email already exists."})
        except User.DoesNotExist:
            pass  # Email doesn't exist, proceed normally
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        existing_banned_user = validated_data.pop('_reregistering_banned_user', None)
        
        if existing_banned_user:
            # Re-register banned user - reset their data
            existing_banned_user.is_banned = False
            existing_banned_user.is_active = True
            existing_banned_user.is_currently_suspicious = False
            existing_banned_user.suspicious_activity_count = 0
            existing_banned_user.last_suspicious_check_date = None
            
            # Clear all previous coffee operations to reset admin table data
            existing_banned_user.coffee_operations.all().delete()
            
            # Update with new data
            for field, value in validated_data.items():
                if field == 'password':
                    existing_banned_user.set_password(value)
                else:
                    setattr(existing_banned_user, field, value)
            
            existing_banned_user.save()
            return existing_banned_user
        else:
            # Create new user normally
            user = User.objects.create_user(**validated_data)
            return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'phone_number', 'address', 'twofa', 'twofa_email', 'is_special_admin')
        read_only_fields = ('id',)

class ProfileSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=False)
    is_profile_complete = serializers.SerializerMethodField()
    missing_fields = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 
                 'current_password', 'new_password', 'new_password_confirm', 'date_joined', 'last_login',
                 'is_profile_complete', 'missing_fields')
        read_only_fields = ('id', 'email', 'date_joined', 'last_login', 'is_profile_complete', 'missing_fields')
        
    def get_is_profile_complete(self, obj):
        """Check if all required profile fields are filled"""
        required_fields = ['first_name', 'last_name', 'username', 'phone_number', 'address']
        for field in required_fields:
            value = getattr(obj, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                return False
        return True
    
    def get_missing_fields(self, obj):
        """Get list of missing required profile fields"""
        required_fields = {
            'first_name': 'First Name',
            'last_name': 'Last Name', 
            'username': 'Username',
            'phone_number': 'Phone Number',
            'address': 'Address'
        }
        missing = []
        for field, display_name in required_fields.items():
            value = getattr(obj, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(display_name)
        return missing
        
    def validate(self, attrs):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        # If any password field is provided, all must be provided
        if any([current_password, new_password, new_password_confirm]):
            if not all([current_password, new_password, new_password_confirm]):
                raise serializers.ValidationError({
                    "password": "To change password, you must provide current password, new password, and confirm new password."
                })
            
            # Verify current password
            if not self.instance.check_password(current_password):
                raise serializers.ValidationError({
                    "current_password": "Current password is incorrect."
                })
            
            # Check if new passwords match
            if new_password != new_password_confirm:
                raise serializers.ValidationError({
                    "new_password": "New password and confirmation don't match."
                })
        
        # Check username uniqueness if being changed
        username = attrs.get('username')
        if username and username != self.instance.username:
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError({
                    "username": "A user with that username already exists."
                })
        
        return attrs
    
    def update(self, instance, validated_data):
        # Handle password change
        current_password = validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        new_password_confirm = validated_data.pop('new_password_confirm', None)
        
        if new_password:
            instance.set_password(new_password)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class AdminUserSerializer(serializers.ModelSerializer):
    is_2fa_enabled = serializers.SerializerMethodField()
    operations = serializers.SerializerMethodField()
    is_suspicious = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                 'address', 'twofa', 'twofa_email', 'is_special_admin', 'is_2fa_enabled',
                 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
                 'operations', 'is_suspicious', 'suspicious_activity_count', 
                 'is_currently_suspicious', 'is_banned', 'last_suspicious_check_date')
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
        """Check if user is currently marked as suspicious or has suspicious activity pattern"""
        # First check if already marked as suspicious
        if obj.is_currently_suspicious:
            return True
            
        # Also check the pattern of operations for display purposes
        try:
            recent_operations = obj.coffee_operations.all()[:10]  # Check last 10 operations
            consecutive_deletes = 0
            
            for operation in recent_operations:
                if operation.operation_type == 'delete':
                    consecutive_deletes += 1
                else:
                    break  # Stop counting if we hit a non-delete operation
            
            return consecutive_deletes >= 5
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