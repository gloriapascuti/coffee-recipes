from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class CoffeeOperation(models.Model):
    OPERATION_TYPES = [
        ('add', 'Add Coffee'),
        ('edit', 'Edit Coffee'),
        ('delete', 'Delete Coffee'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coffee_operations')
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES)
    coffee_id = models.IntegerField(null=True, blank=True)  # May be null for deleted items
    coffee_name = models.CharField(max_length=255, blank=True)  # Store name for deleted items
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.username} - {self.operation_type} - {self.coffee_name or f'Coffee #{self.coffee_id}'} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Check for suspicious activity after saving
        self.check_suspicious_activity()
    
    def check_suspicious_activity(self):
        """Check if user has 5+ consecutive deletes and mark as suspicious if needed"""
        user = self.user
        
        # Get last 10 operations for this user
        recent_operations = user.coffee_operations.all()[:10]
        consecutive_deletes = 0
        
        for operation in recent_operations:
            if operation.operation_type == 'delete':
                consecutive_deletes += 1
            else:
                break  # Stop counting if we hit a non-delete operation
        
        # If user has 5+ consecutive deletes, mark as suspicious
        if consecutive_deletes >= 5 and not user.is_currently_suspicious:
            user.is_currently_suspicious = True
            user.suspicious_activity_count += 1
            user.save(update_fields=['is_currently_suspicious', 'suspicious_activity_count']) 