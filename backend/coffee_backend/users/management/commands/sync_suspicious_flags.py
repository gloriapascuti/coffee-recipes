from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Sync suspicious activity flags for all users based on their recent operations'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        fixed_count = 0
        
        self.stdout.write('Checking all users for suspicious activity inconsistencies...')
        
        for user in users:
            # Check consecutive deletes from recent operations
            recent_operations = user.coffee_operations.all()[:10]
            consecutive_deletes = 0
            
            for operation in recent_operations:
                if operation.operation_type == 'delete':
                    consecutive_deletes += 1
                else:
                    break  # Stop counting if we hit a non-delete operation
            
            # Check if user should be suspicious based on operations
            should_be_suspicious = consecutive_deletes >= 5
            currently_suspicious = user.is_currently_suspicious
            
            if should_be_suspicious and not currently_suspicious:
                # User should be suspicious but isn't marked as such
                user.is_currently_suspicious = True
                user.suspicious_activity_count += 1
                user.save(update_fields=['is_currently_suspicious', 'suspicious_activity_count'])
                
                self.stdout.write(
                    self.style.WARNING(
                        f'Fixed {user.username}: marked as suspicious ({consecutive_deletes} consecutive deletes)'
                    )
                )
                fixed_count += 1
                
            elif not should_be_suspicious and currently_suspicious:
                # User is marked suspicious but shouldn't be based on recent operations
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{user.username}: Currently suspicious but no recent pattern (may have been admin-verified)'
                    )
                )
            else:
                # User status is consistent
                status = "suspicious" if currently_suspicious else "normal"
                self.stdout.write(f'{user.username}: OK ({status})')
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Fixed suspicious activity flags for {fixed_count} users')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All users have consistent suspicious activity flags')
            ) 