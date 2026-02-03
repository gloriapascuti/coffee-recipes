from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from coffee.models.coffee import Coffee


class Command(BaseCommand):
    help = 'Limit each coffee type (by name) to 100 recipes, preserving starred (community winner) recipes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of recipes to keep per coffee type (default: 100)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        
        self.stdout.write(f"Limiting each coffee type to {limit} recipes (preserving starred recipes)")
        
        # Get initial count
        initial_count = Coffee.objects.count()
        self.stdout.write(f'Initial coffee count: {initial_count}')
        
        # Get all coffee types with their counts
        coffee_types = Coffee.objects.values('name').annotate(
            count=Count('id')
        ).filter(count__gt=limit).order_by('name')
        
        if not coffee_types.exists():
            self.stdout.write(self.style.SUCCESS("No coffee types exceed the limit!"))
            return
        
        self.stdout.write(f'\nFound {coffee_types.count()} coffee types exceeding {limit} recipes')
        
        total_to_delete = 0
        ids_to_delete = []
        deletion_summary = []
        
        for coffee_type_data in coffee_types:
            coffee_name = coffee_type_data['name']
            count = coffee_type_data['count']
            excess_count = count - limit
            
            self.stdout.write(f'\nProcessing "{coffee_name}": {count} recipes (excess: {excess_count})')
            
            # Get all recipes of this type
            all_recipes = list(Coffee.objects.filter(name=coffee_name).select_related('origin', 'user'))
            
            # Separate starred and non-starred
            starred_recipes = [c for c in all_recipes if c.is_community_winner]
            non_starred_recipes = [c for c in all_recipes if not c.is_community_winner]
            
            # Sort non-starred by likes count (descending) and then by ID (oldest first)
            non_starred_recipes.sort(key=lambda x: (-x.likes.count(), x.id))
            
            # Calculate how many we can keep from non-starred
            starred_count = len(starred_recipes)
            non_starred_limit = max(0, limit - starred_count)
            
            # Keep all starred + top non-starred up to limit
            recipes_to_keep = starred_recipes + non_starred_recipes[:non_starred_limit]
            recipes_to_delete = non_starred_recipes[non_starred_limit:]
            
            if dry_run:
                self.stdout.write(f'  Starred recipes: {starred_count} (all will be kept)')
                self.stdout.write(f'  Non-starred to keep: {len(recipes_to_keep) - starred_count}')
                self.stdout.write(f'  Non-starred to delete: {len(recipes_to_delete)}')
                
                if recipes_to_delete:
                    first_to_delete = recipes_to_delete[0]
                    self.stdout.write(f'  First to delete: ID {first_to_delete.id} by {first_to_delete.user.username} (likes: {first_to_delete.likes.count()})')
            
            # Collect IDs to delete
            delete_ids = [recipe.id for recipe in recipes_to_delete]
            ids_to_delete.extend(delete_ids)
            total_to_delete += len(delete_ids)
            
            deletion_summary.append({
                'name': coffee_name,
                'total': count,
                'starred': starred_count,
                'to_delete': len(delete_ids),
                'final_count': len(recipes_to_keep)
            })
        
        # Show summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("SUMMARY")
        self.stdout.write("="*60)
        for summary in deletion_summary:
            self.stdout.write(
                f"{summary['name']}: {summary['total']} → {summary['final_count']} "
                f"(starred: {summary['starred']}, deleting: {summary['to_delete']})"
            )
        
        self.stdout.write(f"\nTotal recipes to delete: {total_to_delete}")
        
        # Perform bulk deletion if not dry run
        if not dry_run and ids_to_delete:
            self.stdout.write(f'\nPerforming bulk deletion of {len(ids_to_delete)} records...')
            with transaction.atomic():
                deleted_count = Coffee.objects.filter(id__in=ids_to_delete).delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} recipes'))
            
            # Show final count
            final_count = Coffee.objects.count()
            self.stdout.write(f'Final coffee count: {final_count}')
            self.stdout.write(f'Removed: {initial_count - final_count} recipes')
        elif dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. Use without --dry-run to actually delete.'))
        else:
            self.stdout.write(self.style.SUCCESS('No recipes to delete!'))
