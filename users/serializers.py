class AdminUserTableSerializer(serializers.ModelSerializer):
    """Serializer for admin user table - only accessible by special admin"""
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'is_active', 'is_staff', 
            'is_superuser', 'is_2fa_enabled', 'is_special_admin',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at'] 