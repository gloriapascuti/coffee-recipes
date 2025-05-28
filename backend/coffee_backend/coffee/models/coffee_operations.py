from django.db import models
from django.contrib.auth import get_user_model

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