from django.core.management.base import BaseCommand
from django.db import transaction
from coffee.models.coffee import Coffee, Origin
from collections import defaultdict


class Command(BaseCommand):
    help = 'Remove duplicate coffee entries from the database, keeping the most recent one'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--criteria',
            type=str,
            default='name_origin',
            choices=['name_origin', 'name_only', 'all_fields'],
            help='Criteria for determining duplicates (default: name_origin)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        criteria = options['criteria']
        
        self.stdout.write(f"Looking for duplicate coffees using criteria: {criteria}")
        
        if criteria == 'name_origin':
            duplicates = self.find_duplicates_by_name_and_origin()
        elif criteria == 'name_only':
            duplicates = self.find_duplicates_by_name_only()
        else:  # all_fields
            duplicates = self.find_duplicates_by_all_fields()
        
        total_to_delete = sum(len(group) - 1 for group in duplicates.values() if len(group) > 1)
        
        if total_to_delete == 0:
            self.stdout.write(self.style.SUCCESS("No duplicate coffees found!"))
            return
        
        self.stdout.write(f"\nFound {len(duplicates)} groups of duplicates")
        self.stdout.write(f"Total entries to be deleted: {total_to_delete}")
        
        if dry_run:
            self.show_duplicates_preview(duplicates)
        else:
            self.remove_duplicates(duplicates)
    
    def find_duplicates_by_name_and_origin(self):
        """Find duplicates based on name and origin combination"""
        duplicates = defaultdict(list)
        
        for coffee in Coffee.objects.select_related('origin', 'user').order_by('id'):
            key = (coffee.name.lower().strip(), coffee.origin.name.lower().strip())
            duplicates[key].append(coffee)
        
        return {k: v for k, v in duplicates.items() if len(v) > 1}
    
    def find_duplicates_by_name_only(self):
        """Find duplicates based on name only"""
        duplicates = defaultdict(list)
        
        for coffee in Coffee.objects.select_related('origin', 'user').order_by('id'):
            key = coffee.name.lower().strip()
            duplicates[key].append(coffee)
        
        return {k: v for k, v in duplicates.items() if len(v) > 1}
    
    def find_duplicates_by_all_fields(self):
        """Find duplicates based on all fields (name, origin, description)"""
        duplicates = defaultdict(list)
        
        for coffee in Coffee.objects.select_related('origin', 'user').order_by('id'):
            key = (
                coffee.name.lower().strip(),
                coffee.origin.name.lower().strip(),
                coffee.description.lower().strip()
            )
            duplicates[key].append(coffee)
        
        return {k: v for k, v in duplicates.items() if len(v) > 1}
    
    def show_duplicates_preview(self, duplicates):
        """Show preview of what would be deleted"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("DRY RUN - PREVIEW OF DUPLICATES TO BE REMOVED")
        self.stdout.write("="*60)
        
        for key, coffee_group in duplicates.items():
            if len(coffee_group) > 1:
                self.stdout.write(f"\nDuplicate group: {key}")
                self.stdout.write("-" * 40)
                
                # Sort to show which one will be kept (same logic as removal)
                coffee_group.sort(key=lambda x: (
                    not x.is_community_winner,
                    -x.likes.count(),
                    x.id
                ))
                
                # Show which one will be kept
                kept_coffee = coffee_group[0]
                self.stdout.write(
                    self.style.SUCCESS(
                        f"KEEP:   ID={kept_coffee.id} | {kept_coffee.name} | "
                        f"{kept_coffee.origin.name} | User: {kept_coffee.user.username}"
                    )
                )
                
                # Show which ones will be deleted
                for coffee in coffee_group[1:]:
                    self.stdout.write(
                        self.style.WARNING(
                            f"DELETE: ID={coffee.id} | {coffee.name} | "
                            f"{coffee.origin.name} | User: {coffee.user.username}"
                        )
                    )
        
        self.stdout.write(f"\nTo actually remove duplicates, run without --dry-run flag")
    
    @transaction.atomic
    def remove_duplicates(self, duplicates):
        """Actually remove the duplicate entries"""
        total_deleted = 0
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("REMOVING DUPLICATE COFFEES")
        self.stdout.write("="*60)
        
        for key, coffee_group in duplicates.items():
            if len(coffee_group) > 1:
                # Sort to keep the best one:
                # 1. Community winners first
                # 2. Then by number of likes (descending)
                # 3. Then by ID (oldest first)
                coffee_group.sort(key=lambda x: (
                    not x.is_community_winner,  # False (0) comes before True (1), so winners first
                    -x.likes.count(),  # Negative for descending order
                    x.id  # Oldest first
                ))
                
                # Keep the first one (best one), delete the rest
                kept_coffee = coffee_group[0]
                to_delete = coffee_group[1:]
                
                self.stdout.write(f"\nProcessing group: {key}")
                self.stdout.write(f"Keeping: ID={kept_coffee.id} | {kept_coffee.name}")
                
                for coffee in to_delete:
                    self.stdout.write(f"Deleting: ID={coffee.id} | {coffee.name}")
                    coffee.delete()
                    total_deleted += 1
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Successfully removed {total_deleted} duplicate coffees!")
        )
        
        # Show final statistics
        remaining_count = Coffee.objects.count()
        self.stdout.write(f"Remaining coffee entries: {remaining_count}")
    
    def get_coffee_summary(self, coffee):
        """Get a summary string for a coffee entry"""
        return f"ID={coffee.id} | {coffee.name} | {coffee.origin.name} | User: {coffee.user.username}" 