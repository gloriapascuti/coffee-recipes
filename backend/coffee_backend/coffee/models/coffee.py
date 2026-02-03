from django.db import models
from django.conf import settings

class Origin(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Coffee(models.Model):
    name        = models.CharField(max_length=100)
    origin      = models.ForeignKey(Origin, related_name="coffees", on_delete=models.CASCADE)
    description = models.TextField()
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="coffees",
        on_delete=models.CASCADE,
        default=1    # existing coffees stay tied to the admin user
    )
    is_community_winner = models.BooleanField(default=False)  # Mark recipes that won community challenges
    is_private = models.BooleanField(
        default=False,
        help_text="If True, recipe only appears in owner's recipe list and favorites, not in main recipe list"
    )
    caffeine_mg = models.FloatField(
        default=95.0,
        help_text="Caffeine content in milligrams (default: 95mg for standard cup)"
    )

    @property
    def likes_count(self):
        return self.likes.count()
    
    def get_caffeine_mg(self):
        """Get caffeine content based on coffee name/description (always recalculates)"""
        # Always recalculate based on name/description to ensure accuracy
        # This ensures that even if the stored value is outdated, we get the correct value
        estimated = self._estimate_caffeine_from_name()
        
        # Update the stored value if it's different (for future consistency)
        current_value = self.caffeine_mg or 0
        if abs(current_value - estimated) > 1.0:  # Only update if significantly different
            # Update in database without triggering signals
            if self.pk:
                Coffee.objects.filter(pk=self.pk).update(caffeine_mg=estimated)
                # Update the instance attribute to avoid stale data
                self.caffeine_mg = estimated
        
        return estimated

    def _estimate_caffeine_from_name(self):
        """Estimate caffeine based on coffee name/type using real-world data"""
        name_lower = self.name.lower()
        description_lower = self.description.lower() if self.description else ""
        combined = f"{name_lower} {description_lower}"
        
        # Based on actual caffeine content per serving data
        # Check for specific preparation methods first (most specific)
        if 'cold brew' in combined and ('24' in combined or '24hr' in combined or '24 hour' in combined):
            return 280.0  # Cold brew 24 hrs (250 ml)
        elif 'cold brew' in combined and 'ice' not in combined:
            return 247.0  # Cold brew without ice (250 ml)
        elif 'cold brew' in combined and ('8' in combined or '8hr' in combined or '8 hour' in combined):
            return 238.0  # Cold brew 8 hrs (250 ml)
        elif 'cold brew' in combined:
            return 182.0  # Cold brew with ice (250 ml)
        elif 'french press' in combined:
            return 223.0  # French press (250 ml)
        elif 'aeropress' in combined or 'aero press' in combined:
            return 204.0  # Aeropress (150 ml)
        elif 'pour over' in combined or 'pour-over' in combined or 'v60' in combined:
            return 185.0  # Pour over filter (250 ml)
        elif 'chemex' in combined:
            return 172.0  # Chemex (250 ml)
        elif 'drip' in combined and 'maker' in combined:
            return 170.0  # Drip coffee maker (250 ml)
        elif 'drip' in combined:
            return 116.0  # Drip (200 ml)
        elif 'american press' in combined:
            return 146.0  # American press (250 ml)
        elif 'ristretto' in combined:
            return 63.0  # Ristretto (15 ml)
        elif 'stove-top' in combined or 'stovetop' in combined or 'moka' in combined:
            return 49.0  # Stove-top espresso maker (30 ml)
        elif 'espresso' in combined:
            # Check for double shots
            if 'double' in combined or 'doppio' in combined or '2 shot' in combined or 'two shot' in combined:
                return 136.0  # Double espresso (2 x 68mg)
            return 68.0  # Single espresso (25 ml)
        # Coffee drinks with milk (typically use 1-2 shots of espresso)
        elif 'latte' in combined:
            if 'double' in combined or '2 shot' in combined:
                return 136.0  # Double shot latte
            return 68.0  # Single shot latte (1 espresso shot)
        elif 'cappuccino' in combined:
            if 'double' in combined or '2 shot' in combined:
                return 136.0  # Double shot cappuccino
            return 68.0  # Single shot cappuccino
        elif 'americano' in combined:
            return 95.0  # Americano (espresso + water)
        elif 'macchiato' in combined:
            return 68.0  # Macchiato (espresso with a dash of milk)
        elif 'flat white' in combined:
            if 'double' in combined or '2 shot' in combined:
                return 136.0
            return 68.0
        elif 'decaf' in combined or 'decaffeinated' in combined:
            return 2.0  # Minimal caffeine
        else:
            # Default: assume standard drip coffee
            return 116.0  # Default: standard drip coffee (200 ml)

    def __str__(self):
        return self.name

class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    coffee = models.ForeignKey(
        Coffee,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'coffee')  # Prevent duplicate likes

    def __str__(self):
        return f"{self.user.username} likes {self.coffee.name}"


class ConsumedCoffee(models.Model):
    """Track when a user consumed a coffee recipe"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consumed_coffees"
    )
    coffee = models.ForeignKey(
        Coffee,
        on_delete=models.CASCADE,
        related_name="consumed_by"
    )
    consumed_at = models.DateTimeField(auto_now_add=True)
    # Allow multiple consumptions of the same coffee at different times
    # No unique_together constraint

    class Meta:
        ordering = ['-consumed_at']  # Most recent first
        indexes = [
            models.Index(fields=['user', '-consumed_at']),
        ]

    def __str__(self):
        return f"{self.user.username} consumed {self.coffee.name} at {self.consumed_at}"
