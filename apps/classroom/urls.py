from django.urls import path
from . import views

urlpatterns = [
    path('profesor/', views.teacher_dashboard, name='teacher_dashboard'),
    path('estudiante/', views.student_dashboard, name='student_dashboard'),
    path('mis-logros/', views.student_logros, name='student_logros'),
    path('salon-fama/', views.fame_board, name='fame_board'),
    path('avisos/', views.announcements_view, name='announcements'),
]
