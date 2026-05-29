from django.contrib import admin
from .models import Announcement, FameBoardEntry

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["title", "teacher", "announcement_type", "is_active", "created_at"]
    list_filter = ["announcement_type", "is_active"]

@admin.register(FameBoardEntry)
class FameBoardAdmin(admin.ModelAdmin):
    list_display = ["student", "teacher", "title", "medal_type", "is_active", "created_at"]
    list_filter = ["medal_type", "is_active"]
