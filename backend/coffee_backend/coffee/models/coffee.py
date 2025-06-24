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

    @property
    def likes_count(self):
        return self.likes.count()

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
