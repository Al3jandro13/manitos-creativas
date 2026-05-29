from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/estudiante/', views.register_student_view, name='register_student'),
    path('registro/profesor/', views.register_teacher_view, name='register_teacher'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('perfil/', views.student_profile_view, name='student_profile'),
    path('perfil/profesora/', views.teacher_profile_view, name='teacher_profile'),
    path('correos/', views.send_email_view, name='send_email'),
    path('correos/ia-borrador/', views.ai_draft_email_view, name='ai_draft_email'),
    path('google/desconectar/', views.disconnect_google_view, name='disconnect_google'),
]
