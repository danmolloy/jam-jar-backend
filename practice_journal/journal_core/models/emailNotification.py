from django.db import models
from django.conf import settings

class EmailNotification(models.Model):
    REMINDER = 'reminder'
    GOAL_UPDATE = 'goal_update'
    SUMMARY = 'summary'
    CUSTOM = 'custom'

    TYPE_CHOICES = [
        (REMINDER, 'Reminder'),
        (GOAL_UPDATE, 'Goal Update'),
        (SUMMARY, 'Weekly Summary'),
        (CUSTOM, 'Custom'),
    ]

    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=REMINDER
    )
    sent_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_notifications"
    )
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.notification_type} to {self.sent_to.email} on {self.sent_at.strftime('%Y-%m-%d')}"