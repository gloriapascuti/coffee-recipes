from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    gmail    = models.CharField(max_length=254)
    email    = models.CharField(max_length=254, blank=True, null=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)

    def clean(self):
        # Only allow username='admin' if this is the reserved pk=1 record
        if self.username.lower() == "admin" and (self.pk is None or self.pk != 1):
            raise ValidationError({"username": "Username 'admin' is reserved."})

    class Meta:
        constraints = [
            # Permit "admin" only on the row whose id=1; everywhere else username ≠ "admin"
            models.CheckConstraint(
                condition=Q(id=1) | ~Q(username__iexact="admin"),
                name="username_not_admin_except_reserved"
            ),
        ]

    def __str__(self):
        return self.username


# from django.db import models
# from django.core.exceptions import ValidationError
# from django.db.models import Q
#
# class User(models.Model):
#     username = models.CharField(max_length=150, unique=True)
#     gmail    = models.CharField(max_length=254)
#     password = models.CharField(max_length=128)
#     operations = models.TextField(default='', blank=True)
#
#     def clean(self):
#         # Only allow username='admin' if this is the reserved pk=1 record
#         if self.username.lower() == "admin" and (self.pk is None or self.pk != 1):
#             raise ValidationError({"username": "Username 'admin' is reserved."})
#
#     class Meta:
#         constraints = [
#             # Permit "admin" only on the row whose id=1; everywhere else username ≠ "admin"
#             models.CheckConstraint(
#                 check=Q(id=1) | ~Q(username__iexact="admin"),
#                 name="username_not_admin_except_reserved"
#             ),
#         ]
#
#     def __str__(self):
#         return self.username