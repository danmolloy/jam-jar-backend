from django.db import models
from django.conf import settings

class Goal(models.Model):
    STREAK = 'streak'
    TIME_SPENT = 'time'
    SESSION_COUNT = 'sessions'

    CATEGORY_CHOICES = [
        (STREAK, 'Streak'),
        (TIME_SPENT, 'Time Spent'),
        (SESSION_COUNT, 'Session Count'),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=STREAK,
    )
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    target_count = models.PositiveIntegerField(
        help_text="Target number of days, minutes, or sessions"
    )

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goals"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_goals",
        help_text="Null means user created this goal for themselves"
    )

    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.assigned_to.username})"
