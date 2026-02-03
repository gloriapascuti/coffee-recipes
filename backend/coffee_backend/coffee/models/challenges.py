from django.db import models
from django.conf import settings
from .coffee import Coffee, Origin

class Challenge(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('active', 'Active'),
        ('voting', 'Voting'),
        ('completed', 'Completed'),
    ]
    
    challenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="challenges_made",
        on_delete=models.CASCADE
    )
    challenged = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="challenges_received",
        on_delete=models.CASCADE
    )
    coffee_type = models.CharField(max_length=100)  # e.g., "Filter coffee", "Espresso", etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="challenges_won",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    class Meta:
        unique_together = ('challenger', 'challenged', 'status')  # Prevent duplicate active challenges
    
    def __str__(self):
        return f"{self.challenger.username} challenges {self.challenged.username} - {self.coffee_type}"
    
    @property
    def total_votes(self):
        return self.votes.count()
    
    @property
    def challenger_votes(self):
        return self.votes.filter(voted_for=self.challenger).count()
    
    @property
    def challenged_votes(self):
        return self.votes.filter(voted_for=self.challenged).count()

class ChallengeRecipe(models.Model):
    challenge = models.ForeignKey(Challenge, related_name="recipes", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    origin = models.ForeignKey(Origin, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('challenge', 'user')  # Each user can only submit one recipe per challenge
    
    def __str__(self):
        return f"{self.user.username}'s recipe for {self.challenge.coffee_type}"

class Vote(models.Model):
    challenge = models.ForeignKey(Challenge, related_name="votes", on_delete=models.CASCADE)
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="votes_cast", on_delete=models.CASCADE)
    voted_for = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="votes_received", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('challenge', 'voter')  # Each user can only vote once per challenge
    
    def __str__(self):
        return f"{self.voter.username} voted for {self.voted_for.username} in {self.challenge.coffee_type}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('challenge', 'Challenge Received'),
        ('challenge_accepted', 'Challenge Accepted'),
        ('challenge_declined', 'Challenge Declined'),
        ('recipe_submitted', 'Recipe Submitted'),
        ('voting_started', 'Voting Started'),
        ('challenge_won', 'Challenge Won'),
        ('challenge_lost', 'Challenge Lost'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    challenge = models.ForeignKey(Challenge, related_name="notifications", on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.notification_type}" 