"""
Management command to update caffeine content for existing coffee recipes
based on their names and descriptions using real-world caffeine data.
"""
from django.core.management.base import BaseCommand
from coffee.models.coffee import Coffee


class Command(BaseCommand):
    help = 'Update caffeine content for existing coffee recipes based on their names'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        coffees = Coffee.objects.all()
        updated_count = 0
        
        self.stdout.write(f"Processing {coffees.count()} coffee recipes...")
        
        for coffee in coffees:
            # Get the estimated caffeine using the model's method
            estimated_caffeine = coffee._estimate_caffeine_from_name()
            
            # Only update if the current value is the default or significantly different
            current_caffeine = coffee.caffeine_mg or 0
            
            # Update if it's the default (95.0) or if it's very different from estimate
            if current_caffeine == 95.0 or abs(current_caffeine - estimated_caffeine) > 20:
                if not dry_run:
                    coffee.caffeine_mg = estimated_caffeine
                    coffee.save(update_fields=['caffeine_mg'])
                
                self.stdout.write(
                    f"{'[DRY RUN] Would update' if dry_run else 'Updated'}: "
                    f"{coffee.name} - {current_caffeine}mg -> {estimated_caffeine}mg"
                )
                updated_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[DRY RUN] Would update {updated_count} coffee recipes. '
                    'Run without --dry-run to apply changes.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully updated {updated_count} coffee recipes with accurate caffeine content.'
                )
            )
