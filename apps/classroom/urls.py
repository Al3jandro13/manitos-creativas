from django.urls import path
from . import views

urlpatterns = [
    path('profesor/', views.teacher_dashboard, name='teacher_dashboard'),
    path('estudiante/', views.student_dashboard, name='student_dashboard'),
    path('mis-logros/', views.student_logros, name='student_logros'),
    path('salon-fama/', views.fame_board, name='fame_board'),
    path('avisos/', views.announcements_view, name='announcements'),
    path('cursos/', views.teacher_courses, name='teacher_courses'),
    path('cursos/<int:pk>/', views.teacher_course_detail, name='teacher_course_detail'),
    path('cursos/nuevo-estudiante/', views.teacher_create_student, name='teacher_create_student'),
]
