from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

achievements = [
    {"id": 1, "name": "First Practice", "description": "Complete your first practice session", "type": "streak", "value": 1},
    {"id": 2, "name": "2-Day Streak", "description": "Practice 2 days in a row", "type": "streak", "value": 2},
    {"id": 3, "name": "7-Day Streak", "description": "Practice 7 days in a row", "type": "streak", "value": 7},
    {"id": 4, "name": "30-Day Streak", "description": "Practice 30 days in a row", "type": "streak", "value": 30},
]

class PracticeItem(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="practice_items"
    )

    date = models.DateField(auto_now_add=True)
    activity = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    duration = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(180)]
    )
    recording = models.FileField(upload_to="recordings/", blank=True, null=True)
    teacher_feedback = models.TextField(blank=True)
    tags = ArrayField(
            models.CharField(max_length=50),
            blank=True,
            default=list,
            help_text="List of hashtags"
        )
    points_awarded = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )

    def award_achievements(self):
        if not hasattr(self.student, "achievements"):
            return

        current_achievements = self.student.achievements or []

        eligible = [
            a for a in achievements
            if a["type"] == "streak"
            #and a["value"] <= self.student.current_streak
            and a["id"] not in current_achievements
        ]

        if eligible:
            new_ids = [a["id"] for a in eligible]
            self.student.achievements.extend(new_ids)
            self.student.save()


