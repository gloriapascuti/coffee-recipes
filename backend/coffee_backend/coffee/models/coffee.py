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
    caffeine_mg = models.FloatField(
        default=95.0,
        help_text="Caffeine content in milligrams (default: 95mg for standard cup)"
    )

    @property
    def likes_count(self):
        return self.likes.count()
    
    def get_caffeine_mg(self):
        """Get caffeine content, with fallback to default if not set"""
        if self.caffeine_mg:
            return self.caffeine_mg
        # Fallback: estimate based on common coffee types
        return self._estimate_caffeine_from_name()

    def _estimate_caffeine_from_name(self):
        """Estimate caffeine based on coffee name/type"""
        name_lower = self.name.lower()
        # Common caffeine estimates (mg per serving)
        if 'espresso' in name_lower:
            return 64.0  # Single shot
        elif 'double' in name_lower or 'doppio' in name_lower:
            return 128.0  # Double shot
        elif 'americano' in name_lower:
            return 95.0
        elif 'latte' in name_lower or 'cappuccino' in name_lower:
            return 77.0  # With milk
        elif 'cold brew' in name_lower:
            return 200.0  # Typically stronger
        elif 'decaf' in name_lower or 'decaffeinated' in name_lower:
            return 2.0  # Minimal caffeine
        else:
            return 95.0  # Default: standard cup

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
