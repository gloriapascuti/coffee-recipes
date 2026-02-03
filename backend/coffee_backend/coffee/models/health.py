from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class UserHealthProfile(models.Model):
    """User health profile for heart disease prediction"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="health_profile"
    )
    
    # Demographics
    sex = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Physical measurements
    height_cm = models.FloatField(
        validators=[MinValueValidator(50), MaxValueValidator(250)],
        blank=True,
        null=True,
        help_text="Height in centimeters"
    )
    weight_kg = models.FloatField(
        validators=[MinValueValidator(20), MaxValueValidator(300)],
        blank=True,
        null=True,
        help_text="Weight in kilograms"
    )
    
    # Family history
    has_family_history_chd = models.BooleanField(default=False, help_text="Family history of coronary heart disease")
    num_relatives_chd = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Number of relatives with CHD"
    )
    family_history_details = models.TextField(blank=True, null=True, help_text="Details about family history")
    
    # Medical conditions
    has_hypertension = models.BooleanField(default=False)
    has_diabetes = models.BooleanField(default=False)
    has_high_cholesterol = models.BooleanField(default=False)
    has_obesity = models.BooleanField(default=False)
    
    # Lifestyle
    is_smoker = models.BooleanField(default=False)
    activity_level = models.CharField(
        max_length=20,
        choices=[
            ('sedentary', 'Sedentary'),
            ('light', 'Light'),
            ('moderate', 'Moderate'),
            ('active', 'Active'),
            ('very_active', 'Very Active')
        ],
        blank=True,
        null=True
    )
    
    # Other health issues
    other_health_issues = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def age(self):
        """Calculate age from date_of_birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    @property
    def bmi(self):
        """Calculate BMI from height and weight"""
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 2)
        return None
    
    def __str__(self):
        return f"Health profile for {self.user.username}"


class BloodPressureEntry(models.Model):
    """Blood pressure readings for users"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blood_pressure_entries"
    )
    systolic = models.IntegerField(
        validators=[MinValueValidator(70), MaxValueValidator(250)],
        help_text="Systolic pressure (big number)"
    )
    diastolic = models.IntegerField(
        validators=[MinValueValidator(40), MaxValueValidator(150)],
        help_text="Diastolic pressure (small number)"
    )
    pulse = models.IntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        blank=True,
        null=True,
        help_text="Heart rate/pulse"
    )
    measured_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-measured_at']
        indexes = [
            models.Index(fields=['user', '-measured_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.systolic}/{self.diastolic} at {self.measured_at}"
