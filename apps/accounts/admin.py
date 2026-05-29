from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TeacherProfile, StudentProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter   = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    fieldsets     = UserAdmin.fieldsets + (
        ('Rol en Manitos Creativas', {'fields': ('role',)}),
    )


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'level', 'age', 'selected_avatar', 'total_stars', 'total_medals', 'parent_name']
    list_filter   = ['level', 'selected_avatar']
    search_fields = ['user__username', 'user__first_name', 'parent_name']
