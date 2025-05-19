# coffee/models/user_profile.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user              = models.OneToOneField(User, on_delete=models.CASCADE)
    users_operations  = models.TextField(default='', blank=True)
