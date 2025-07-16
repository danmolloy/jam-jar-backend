from django.contrib import admin
from .models import CustomUser, PracticeItem, Goal, EmailNotification

admin.site.register([CustomUser,  PracticeItem, Goal, EmailNotification])