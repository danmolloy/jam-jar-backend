from django.db import models
from django.conf import settings

class DiaryEntry(models.Model):
  author = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="diary_entries"
  )
  date = models.DateTimeField(auto_now_add=True)
  title = models.CharField(max_length=50)
  body = models.TextField(blank=False)
  created_at = models.DateTimeField(auto_now_add=True)
