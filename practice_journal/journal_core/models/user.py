from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    timezone = models.CharField(max_length=100, default="Europe/London")
    subscription_id = models.CharField(max_length=100, blank=True, null=True)
    subscription_status = models.CharField(null=True)
    daily_target = models.IntegerField(default=0)
    #current_streak = models.IntegerField(default=0)
    #longest_streak = models.IntegerField(default=0)
    achievements = ArrayField(models.IntegerField(), default=list)
   


