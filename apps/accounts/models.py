from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'Profesor/a'),
        ('student', 'Estudiante'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='teacher_profile'
    )
    bio = models.TextField(blank=True)
    subject_specialty = models.CharField(max_length=100, blank=True)
    years_experience = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Perfil de Profesor'
        verbose_name_plural = 'Perfiles de Profesores'

    def __str__(self):
        return f"Profe: {self.user.get_full_name()}"


class StudentProfile(models.Model):
    LEVEL_CHOICES = [
        ('A', 'Transición A'),
        ('B', 'Transición B'),
    ]
    AVATAR_CHOICES = [
        ('mochi', 'Mochi 🩷'),
        ('kiko', 'Kiko 🧡'),
        ('star', 'Estrella ⭐'),
        ('cloud', 'Nube ☁️'),
    ]

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='student_profile'
    )
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES, default='A')
    age = models.PositiveIntegerField(default=5)
    parent_name = models.CharField(max_length=150)
    parent_email = models.EmailField()
    parent_phone = models.CharField(max_length=20, blank=True)
    selected_avatar = models.CharField(max_length=20, choices=AVATAR_CHOICES, default='mochi')
    total_stars = models.PositiveIntegerField(default=0)
    total_medals = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Perfil de Estudiante'
        verbose_name_plural = 'Perfiles de Estudiantes'

    def __str__(self):
        return f"{self.user.get_full_name()} — Nivel {self.level}"

    def add_stars(self, amount):
        self.total_stars += amount
        self.save(update_fields=['total_stars'])
