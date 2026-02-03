from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db import transaction
from coffee.models.coffee import Coffee
from collections import defaultdict


class Command(BaseCommand):
    help = 'Remove excess coffee recipes to ensure no more than 1000 recipes have the same name'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Maximum number of recipes allowed per name (default: 1000)',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the deletion (required for actual deletion)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        confirm = options['confirm']

        if not dry_run and not confirm:
            self.stdout.write(
                self.style.ERROR(
                    'You must use either --dry-run to preview or --confirm to actually delete excess recipes'
                )
            )
            return

        self.stdout.write(self.style.SUCCESS(f'Starting process to limit recipes to {limit} per name...'))
        
        # Get initial count
        initial_count = Coffee.objects.count()
        self.stdout.write(f'Initial coffee count: {initial_count}')

        # Find coffee names that have more than the limit
        coffee_names_over_limit = Coffee.objects.values('name').annotate(
            count=Count('id')
        ).filter(count__gt=limit).order_by('-count')

        if not coffee_names_over_limit:
            self.stdout.write(self.style.SUCCESS(f'No coffee names have more than {limit} recipes. Nothing to do!'))
            return

        self.stdout.write(f'Found {len(coffee_names_over_limit)} coffee names with more than {limit} recipes')

        total_to_delete = 0
        deletion_summary = []
        ids_to_delete = []

        # Process each coffee name that exceeds the limit
        for coffee_name_data in coffee_names_over_limit:
            name = coffee_name_data['name']
            count = coffee_name_data['count']
            excess_count = count - limit

            self.stdout.write(f'\nProcessing "{name}": {count} recipes (excess: {excess_count})')

            # Get all recipes with this name, ordered by ID (oldest first)
            recipes_with_name = Coffee.objects.filter(name=name).order_by('id')
            
            # Convert to lists to avoid queryset slicing issues
            all_recipes = list(recipes_with_name)
            recipes_to_keep = all_recipes[:limit]
            recipes_to_delete = all_recipes[limit:]

            if dry_run:
                self.stdout.write(f'  Would keep {len(recipes_to_keep)} oldest recipes')
                self.stdout.write(f'  Would delete {len(recipes_to_delete)} newest recipes')
                
                # Show some examples of what would be kept and deleted
                if recipes_to_keep:
                    oldest = recipes_to_keep[0]
                    newest_kept = recipes_to_keep[-1]
                    self.stdout.write(f'  Oldest to keep: ID {oldest.id} by {oldest.user.username}')
                    self.stdout.write(f'  Newest to keep: ID {newest_kept.id} by {newest_kept.user.username}')
                
                if recipes_to_delete:
                    first_to_delete = recipes_to_delete[0]
                    self.stdout.write(f'  First to delete: ID {first_to_delete.id} by {first_to_delete.user.username}')

            # Collect IDs to delete
            delete_ids = [recipe.id for recipe in recipes_to_delete]
            ids_to_delete.extend(delete_ids)
            total_to_delete += len(delete_ids)

            deletion_summary.append({
                'name': name,
                'original_count': count,
                'to_delete': len(delete_ids),
                'final_count': len(recipes_to_keep)
            })

        # Perform bulk deletion if not dry run
        if not dry_run and ids_to_delete:
            self.stdout.write(f'\nPerforming bulk deletion of {len(ids_to_delete)} excess records...')
            with transaction.atomic():
                deleted_count = Coffee.objects.filter(id__in=ids_to_delete).delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} excess records'))

        # Show detailed summary
        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN SUMMARY ==='))
            self.stdout.write(f'Would delete: {total_to_delete} excess recipes')
            self.stdout.write(f'Final count would be: {initial_count - total_to_delete}')
        else:
            final_count = Coffee.objects.count()
            actual_deleted = initial_count - final_count
            
            self.stdout.write(self.style.SUCCESS('\n=== DELETION COMPLETE ==='))
            self.stdout.write(f'Deleted: {actual_deleted} excess recipes')
            self.stdout.write(f'Remaining: {final_count} total recipes')

        # Show breakdown by coffee name
        self.stdout.write('\n=== BREAKDOWN BY COFFEE NAME ===')
        self.stdout.write(f'{"Coffee Name":<30} {"Original":<10} {"Deleted":<10} {"Final":<10}')
        self.stdout.write('-' * 60)
        
        for summary in deletion_summary[:10]:  # Show top 10 most affected
            self.stdout.write(
                f'{summary["name"]:<30} {summary["original_count"]:<10} '
                f'{summary["to_delete"]:<10} {summary["final_count"]:<10}'
            )
        
        if len(deletion_summary) > 10:
            self.stdout.write(f'... and {len(deletion_summary) - 10} more coffee names')

        # Verify no names exceed the limit after operation
        if not dry_run:
            remaining_over_limit = Coffee.objects.values('name').annotate(
                count=Count('id')
            ).filter(count__gt=limit)
            
            if remaining_over_limit.exists():
                self.stdout.write(
                    self.style.ERROR(f'Warning: {len(remaining_over_limit)} names still exceed the limit!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Confirmed: No coffee names exceed {limit} recipes')
                )

        self.stdout.write(self.style.SUCCESS('\nProcess completed successfully!'))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nTo actually perform the deletion, run:\n'
                    f'python manage.py limit_duplicate_names --limit {limit} --confirm'
                )
            ) 