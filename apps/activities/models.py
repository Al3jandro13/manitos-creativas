from django.db import models
from django.utils import timezone
from apps.accounts.models import CustomUser


class ActivityCategory(models.Model):
    CATEGORY_CHOICES = [
        ('colorear', '🎨 Colorear'),
        ('puntillismo', '✏️ Puntillismo'),
        ('rompecabezas', '🧩 Rompecabezas'),
        ('cuento', '📚 Cuento Interactivo'),
        ('dibujo_libre', '✍️ Dibujo Libre'),
        ('consonantes', '🔤 Consonantes'),
        ('numeros', '🔢 Números 1-100'),
        ('sumas', '➕ Sumas'),
        ('restas', '➖ Restas'),
        ('lenguaje_senas', '🤟 Lenguaje de Señas'),
        ('exploracion', '🔭 Exploración'),
        ('actividad_libre', '⭐ Actividad Libre'),
    ]

    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    icon = models.CharField(max_length=10, default='⭐')
    color = models.CharField(max_length=7, default='#FF6B6B')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.get_name_display()


class Activity(models.Model):
    DIFFICULTY_CHOICES = [
        (1, '⭐ Muy Fácil'),
        (2, '⭐⭐ Fácil'),
        (3, '⭐⭐⭐ Medio'),
        (4, '⭐⭐⭐⭐ Difícil'),
        (5, '⭐⭐⭐⭐⭐ Muy Difícil'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicada'),
        ('archived', 'Archivada'),
    ]

    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción')
    category = models.ForeignKey(
        ActivityCategory, on_delete=models.CASCADE, related_name='activities'
    )
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='created_activities'
    )
    difficulty = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_CHOICES, default=1, verbose_name='Dificultad'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft'
    )
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha límite')
    reward_stars = models.PositiveIntegerField(default=3, verbose_name='Estrellas de recompensa')
    reward_sticker = models.CharField(max_length=50, default='star', verbose_name='Sticker de recompensa')
    instructions = models.TextField(blank=True, verbose_name='Instrucciones adicionales')
    image = models.ImageField(upload_to='activities/', blank=True, null=True)
    assigned_to_all = models.BooleanField(default=True)
    assigned_students = models.ManyToManyField(
        CustomUser, related_name='assigned_activities', blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date:
            return timezone.now() > self.due_date
        return False

    @property
    def submission_count(self):
        return self.submissions.filter(status__in=['submitted', 'reviewed', 'approved']).count()


class ActivityAttachment(models.Model):
    TYPES = [
        ('image', 'Imagen'),
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='activity_attachments/')
    file_type = models.CharField(max_length=20, choices=TYPES)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ActivitySubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('submitted', 'Enviada'),
        ('reviewed', 'Revisada'),
        ('approved', '¡Aprobada! ⭐'),
    ]

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(null=True, blank=True)
    content = models.TextField(blank=True)
    drawing_data = models.TextField(blank=True)  # JSON canvas data
    image = models.ImageField(upload_to='submissions/', blank=True, null=True)
    teacher_feedback = models.TextField(blank=True)
    stars_awarded = models.PositiveIntegerField(default=0)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False, verbose_name='En salón de la fama')

    class Meta:
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'
        unique_together = ['activity', 'student']

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.activity.title}"
