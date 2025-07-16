from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

class AudioRecording(models.Model):
  id = models.AutoField(primary_key=True)
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="recordings"
  )
  s3_key = models.CharField(max_length=1024) 
  title = models.CharField(max_length=255)
  notes = models.TextField(blank=True)
  tags = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
    )
  date = models.DateField(auto_now_add=True)
  location = models.CharField(max_length=255, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.title} - {self.date}"