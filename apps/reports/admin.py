from django.contrib import admin
from .models import GradeRecord, WeeklyReport

@admin.register(GradeRecord)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["student", "teacher", "subject", "period", "grade", "performance", "created_at"]
    list_filter = ["performance", "period"]

@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ["student", "teacher", "week_start", "week_end", "average_score"]
