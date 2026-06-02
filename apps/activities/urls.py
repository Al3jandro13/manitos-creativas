from django.urls import path
from . import views

urlpatterns = [
    # Teacher
    path('', views.teacher_activity_list, name='activities_list'),
    path('crear/', views.teacher_activity_create, name='create_activity'),
    path('entregas/', views.submissions_overview, name='submissions_overview'),
    path('revision/<int:submission_id>/destacar/', views.quick_feature_submission, name='quick_feature_submission'),
    path('<int:pk>/', views.teacher_activity_detail, name='activity_detail'),
    path('<int:pk>/editar/', views.teacher_activity_edit, name='activity_edit'),
    path('<int:pk>/eliminar/', views.teacher_activity_delete, name='activity_delete'),
    path('revision/<int:submission_id>/', views.review_submission, name='review_submission'),
    # Student
    path('mis-tareas/', views.student_activities, name='student_activities'),
    path('tarea/<int:pk>/', views.student_activity_detail, name='student_activity_detail'),
    path('entrega/<int:pk>/eliminar/', views.student_delete_submission, name='student_delete_submission'),
    # Coop — Teacher
    path('parejas/', views.coop_list, name='coop_list'),
    path('parejas/crear/', views.coop_create, name='coop_create'),
    path('parejas/<int:pk>/', views.coop_detail, name='coop_detail'),
    path('parejas/<int:pk>/editar/', views.coop_edit, name='coop_edit'),
    path('parejas/<int:pk>/eliminar/', views.coop_delete, name='coop_delete'),
    path('parejas/<int:coop_pk>/revisar/', views.coop_review, name='coop_review'),
    # Coop — Student
    path('mis-parejas/', views.student_coop_list, name='student_coop_list'),
    path('mis-parejas/<int:pk>/', views.student_coop_work, name='student_coop_work'),
]
