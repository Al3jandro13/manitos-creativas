from django.urls import path
from . import views

urlpatterns = [
    # Teacher
    path('', views.teacher_activity_list, name='activities_list'),
    path('crear/', views.teacher_activity_create, name='create_activity'),
    path('<int:pk>/', views.teacher_activity_detail, name='activity_detail'),
    path('revision/<int:submission_id>/', views.review_submission, name='review_submission'),
    # Student
    path('mis-tareas/', views.student_activities, name='student_activities'),
    path('tarea/<int:pk>/', views.student_activity_detail, name='student_activity_detail'),
]
