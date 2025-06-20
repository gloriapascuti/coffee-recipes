from rest_framework import serializers
from .models import CustomUser

class CoffeeOperationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('operation_type', 'coffee_id', 'coffee_name', 'timestamp')

# Import after to avoid circular imports
try:
    from coffee.models.coffee_operations import CoffeeOperation
    CoffeeOperationSerializer.Meta.model = CoffeeOperation
except ImportError:
    pass

class AdminUserTableSerializer(serializers.ModelSerializer):
    """Serializer for admin user table - only accessible by special admin"""
    operations = serializers.SerializerMethodField()
    is_suspicious = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'is_active', 'is_staff', 
            'is_superuser', 'is_2fa_enabled', 'is_special_admin',
            'date_joined', 'last_login', 'created_at', 'updated_at',
            'operations', 'is_suspicious'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
    
    def get_operations(self, obj):
        """Get recent coffee operations for this user"""
        try:
            operations = obj.coffee_operations.all()[:10]  # Last 10 operations
            return CoffeeOperationSerializer(operations, many=True).data
        except Exception as e:
            print(f"Error getting operations for user {obj.id}: {e}")
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
        except Exception as e:
            print(f"Error checking suspicious activity for user {obj.id}: {e}")
            return False 