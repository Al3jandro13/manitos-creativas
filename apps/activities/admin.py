from django.contrib import admin
from .models import ActivityCategory, Activity, ActivitySubmission, ActivityAttachment


@admin.register(ActivityCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'teacher', 'status', 'difficulty', 'reward_stars', 'created_at']
    list_filter = ['status', 'category', 'difficulty']
    search_fields = ['title', 'description']


@admin.register(ActivitySubmission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'activity', 'status', 'stars_awarded', 'submitted_at', 'is_featured']
    list_filter = ['status', 'is_featured']
