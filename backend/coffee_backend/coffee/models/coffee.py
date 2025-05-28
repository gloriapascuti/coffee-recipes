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

    def __str__(self):
        return self.name
