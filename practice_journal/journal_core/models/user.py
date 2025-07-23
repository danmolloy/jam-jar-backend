from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    timezone = models.CharField(max_length=100, default="Europe/London")
    subscription_id = models.CharField(max_length=100, blank=True, null=True)
    subscription_status = models.CharField(null=True, max_length=50)
    daily_target = models.IntegerField(default=0)
    #current_streak = models.IntegerField(default=0)
    #longest_streak = models.IntegerField(default=0)
    achievements = ArrayField(models.IntegerField(), default=list)
    
    # Email confirmation fields
    email_confirmed = models.BooleanField(default=False)
    email_confirmation_token = models.CharField(max_length=100, blank=True, null=True)
    email_confirmation_sent_at = models.DateTimeField(blank=True, null=True)
    
    def generate_email_confirmation_token(self):
        """Generate a unique token for email confirmation"""
        import secrets
        self.email_confirmation_token = secrets.token_urlsafe(32)
        self.email_confirmation_sent_at = timezone.now()
        self.save(update_fields=['email_confirmation_token', 'email_confirmation_sent_at'])
        return self.email_confirmation_token
    
    def is_email_confirmation_token_valid(self):
        """Check if the email confirmation token is still valid (24 hours)"""
        if not self.email_confirmation_sent_at:
            return False
        return timezone.now() - self.email_confirmation_sent_at < timedelta(hours=24)
   


