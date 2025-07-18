from django.contrib import admin
from .models import CustomUser, PracticeItem, Goal, EmailNotification, DiaryEntry

admin.site.register([CustomUser,  PracticeItem, Goal, EmailNotification, DiaryEntry])