# # coffee/signals.py
#
# from django.apps import apps
# from django.db.models.signals import post_migrate, post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from .models import UserProfile
#
# @receiver(post_migrate)
# def create_admin_user(sender, **kwargs):
#     """
#     After all apps have migrated, ensure the 'admin' superuser exists.
#     Only run once, and only when the auth app is ready.
#     """
#     # only run when the auth app has just migrated
#     if sender.name == 'auth':
#         User = apps.get_model('auth', 'User')
#         if not User.objects.filter(username='admin').exists():
#             User.objects.create_superuser(
#                 username='admin',
#                 email='admin@example.com',
#                 password='admin'
#             )
#
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#


# coffee/signals.py

import sys
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models.coffee import Coffee
from .models.user_profile import UserProfile

User = get_user_model()

def _log_profile_op(user, op):
    # Debug
    print(f"[signals] → _log_profile_op: user={user.pk}, op={op}", file=sys.stderr)

    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        print(f"[signals] ‼️ Created new profile for user {user.pk}", file=sys.stderr)

    before = profile.users_operations
    after = f"{before},{op}" if before else op
    profile.users_operations = after
    profile.save(update_fields=['users_operations'])

    print(f"[signals] ✅ profile.users_operations: before='{before}' → after='{after}'", file=sys.stderr)


@receiver(post_save, sender=Coffee)
def on_coffee_saved(sender, instance, created, **kwargs):
    op = 'add' if created else 'edit'
    print(f"[signals] post_save: Coffee id={instance.pk}, user={instance.user.pk}, op={op}", file=sys.stderr)
    _log_profile_op(instance.user, op)


@receiver(post_delete, sender=Coffee)
def on_coffee_deleted(sender, instance, **kwargs):
    print(f"[signals] post_delete: Coffee id={instance.pk}, user={instance.user.pk}", file=sys.stderr)
    _log_profile_op(instance.user, 'delete')
