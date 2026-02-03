from django.core.management.base import BaseCommand
from django.db.models import Count, Min
from coffee.models.coffee import Coffee
from django.db import transaction


class Command(BaseCommand):
    help = 'Remove duplicate coffee recipes, keeping only one unique recipe per name-origin combination'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the deletion (required for actual deletion)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        confirm = options['confirm']

        if not dry_run and not confirm:
            self.stdout.write(
                self.style.ERROR(
                    'You must use either --dry-run to preview or --confirm to actually delete duplicates'
                )
            )
            return

        self.stdout.write(self.style.SUCCESS('Starting duplicate recipe removal process...'))
        
        # Get initial count
        initial_count = Coffee.objects.count()
        self.stdout.write(f'Initial coffee count: {initial_count}')

        # Find duplicates based on name and origin
        duplicates = Coffee.objects.values('name', 'origin').annotate(
            count=Count('id'),
            min_id=Min('id')
        ).filter(count__gt=1)

        duplicate_count = len(duplicates)
        self.stdout.write(f'Found {duplicate_count} name-origin combinations with duplicates')

        total_to_delete = 0
        recipes_to_keep = []
        ids_to_delete = []
        
        # Collect all IDs to delete in a single pass
        for duplicate in duplicates:
            name = duplicate['name']
            origin_id = duplicate['origin']
            count = duplicate['count']
            min_id = duplicate['min_id']  # Keep the oldest entry (lowest ID)
            
            # Find all coffee entries for this name-origin combination
            coffee_entries = Coffee.objects.filter(
                name=name, 
                origin_id=origin_id
            ).order_by('id')
            
            # Keep the first (oldest) entry, mark others for deletion
            entries_to_delete = coffee_entries.exclude(id=min_id)
            delete_count = entries_to_delete.count()
            total_to_delete += delete_count
            
            # Collect IDs to delete
            ids_to_delete.extend(list(entries_to_delete.values_list('id', flat=True)))
            
            if coffee_entries.exists():
                keeper = coffee_entries.first()
                recipes_to_keep.append({
                    'id': keeper.id,
                    'name': keeper.name,
                    'origin': keeper.origin.name,
                    'description': keeper.description[:50] + '...' if len(keeper.description) > 50 else keeper.description
                })

            if dry_run:
                self.stdout.write(
                    f'Would delete {delete_count} duplicates of "{name}" from {origin_id}, keeping ID {min_id}'
                )

        # Perform bulk deletion if not dry run
        if not dry_run and ids_to_delete:
            self.stdout.write(f'Performing bulk deletion of {len(ids_to_delete)} records...')
            with transaction.atomic():
                Coffee.objects.filter(id__in=ids_to_delete).delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {len(ids_to_delete)} duplicate records'))

        # Show summary
        unique_recipes = len(recipes_to_keep)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN SUMMARY ==='))
            self.stdout.write(f'Would delete: {total_to_delete} duplicate entries')
            self.stdout.write(f'Would keep: {unique_recipes} unique recipes')
            self.stdout.write(f'Final count would be: {initial_count - total_to_delete}')
            self.stdout.write('\nTop 10 recipes that would be kept:')
            for i, recipe in enumerate(recipes_to_keep[:10], 1):
                self.stdout.write(f"{i}. ID {recipe['id']}: {recipe['name']} ({recipe['origin']}) - {recipe['description']}")
        else:
            final_count = Coffee.objects.count()
            deleted_count = initial_count - final_count
            
            self.stdout.write(self.style.SUCCESS('\n=== DELETION COMPLETE ==='))
            self.stdout.write(f'Deleted: {deleted_count} duplicate entries')
            self.stdout.write(f'Remaining: {final_count} unique recipes')
            self.stdout.write(f'Unique name-origin combinations: {Coffee.objects.values("name", "origin").distinct().count()}')

        self.stdout.write(self.style.SUCCESS('\nProcess completed successfully!'))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\nTo actually perform the deletion, run:\n'
                    'python manage.py remove_duplicate_recipes --confirm'
                )
            ) 