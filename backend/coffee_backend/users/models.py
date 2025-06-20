from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    totp_secret = models.CharField(max_length=100, blank=True, null=True)
    twofa = models.BooleanField(default=False)
    twofa_email = models.EmailField(blank=True, null=True)
    is_special_admin = models.BooleanField(default=False)
    
    # Suspicious activity tracking fields
    suspicious_activity_count = models.IntegerField(default=0)  # Count of times marked as suspicious
    is_currently_suspicious = models.BooleanField(default=False)  # Currently under investigation
    is_banned = models.BooleanField(default=False)  # User is banned
    last_suspicious_check_date = models.DateTimeField(null=True, blank=True)  # Last time admin checked

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email
