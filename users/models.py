from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    totp_secret = models.CharField(max_length=100, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    is_special_admin = models.BooleanField(default=False)  # Only for MacBook owner
    plain_password = models.CharField(max_length=128, blank=True, null=True)  # Store plain text password

    # Add related_name to avoid clashes with the default User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def set_password(self, raw_password):
        """Override to store plain text password"""
        self.plain_password = raw_password
        # Still set the encrypted password for Django compatibility
        super().set_password(raw_password)

    def check_password(self, raw_password):
        """Override to check against plain text password"""
        return self.plain_password == raw_password

    def __str__(self):
        return self.email 