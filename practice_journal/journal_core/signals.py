from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PracticeItem
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

""" @receiver(post_save, sender=PracticeItem)
def update_practice_streak(sender, instance, created, **kwargs):
    if not created:
        return  

    user = instance.student
    today = instance.date
    yesterday = today - timedelta(days=1)

    practiced_yesterday = PracticeItem.objects.filter(student=user, date=yesterday).exists()
    practiced_today_already = PracticeItem.objects.filter(student=user, date=today).count() > 1

    if practiced_today_already:
        return  

    if practiced_yesterday:
        user.current_streak += 1
    else:
        user.current_streak = 1  

    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak

    user.save() """