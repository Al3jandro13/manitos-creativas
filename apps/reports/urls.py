from django.urls import path
from . import views

urlpatterns = [
    path('notas/', views.grades_view, name='grades'),
    path('semanales/', views.weekly_reports_view, name='weekly_reports'),
]
