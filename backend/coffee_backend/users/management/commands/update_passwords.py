from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Update passwords for all users according to specified rules'

    def handle(self, *args, **options):
        # Get all users
        users = CustomUser.objects.all()
        
        if not users:
            self.stdout.write(self.style.WARNING('No users found in the database'))
            return
        
        updated_count = 0
        
        for user in users:
            if user.username == 'filip_admin':
                # Admin gets password 135908
                new_password = '135908'
                self.stdout.write(f'Setting admin password for {user.username}')
            else:
                # Non-admin users get their username as password
                # If username is too short, double it
                if len(user.username) < 6:
                    new_password = user.username + user.username
                    self.stdout.write(f'Setting doubled password for {user.username}: {new_password}')
                else:
                    new_password = user.username
                    self.stdout.write(f'Setting username password for {user.username}: {new_password}')
            
            # Hash and set the password
            user.password = make_password(new_password)
            user.save()
            updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated passwords for {updated_count} users')
        ) 