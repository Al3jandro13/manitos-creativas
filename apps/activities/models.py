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
        ('numeros', '🔢 Números'),
        ('sumas', '➕ Sumas'),
        ('restas', '➖ Restas'),
        ('serpiente', '🐍 Serpiente'),
        ('sopa_letras', '🔠 Sopa de Letras'),
        # Juegos individuales nuevos
        ('memoria', '🃏 Memoria Visual'),
        ('contar_objetos', '🔢 Contar Objetos'),
        ('figuras', '🔷 Figuras Geométricas'),
        # Actividades en pareja nuevas
        ('sopa_letras_coop', '🔠 Sopa de Letras en Pareja'),
        ('cuento_coop', '📖 Cuento en Pareja'),
        ('mural_coop', '🖼️ Mural Colaborativo'),
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


class CoopActivity(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicada'),
        ('archived', 'Archivada'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='coop_activities'
    )
    student1 = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='coop_as_student1'
    )
    student2 = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='coop_as_student2'
    )
    instructions = models.TextField(blank=True)
    reward_stars = models.PositiveIntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    coloring_image = models.ForeignKey(
        'games.ColoringImage',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='coop_activities',
    )
    puzzle_image = models.ForeignKey(
        'games.PuzzleImage',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='coop_activities',
    )
    puzzle_rows = models.PositiveSmallIntegerField(default=2)
    puzzle_cols = models.PositiveSmallIntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Actividad en Pareja'
        verbose_name_plural = 'Actividades en Parejas'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CoopSubmission(models.Model):
    STEP_CHOICES = [(1, 'Parte 1'), (2, 'Parte 2')]
    STATUS_CHOICES = [
        ('waiting', 'Esperando'),
        ('in_progress', 'En progreso'),
        ('submitted', 'Enviado'),
        ('reviewed', 'Revisado'),
        ('approved', 'Aprobado'),
    ]

    coop_activity = models.ForeignKey(
        CoopActivity, on_delete=models.CASCADE, related_name='submissions'
    )
    student = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='coop_submissions'
    )
    step = models.PositiveSmallIntegerField(choices=STEP_CHOICES)
    drawing_data = models.TextField(blank=True)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    submitted_at = models.DateTimeField(null=True, blank=True)
    teacher_feedback = models.TextField(blank=True)
    stars_awarded = models.PositiveIntegerField(default=0)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Envío Colaborativo'
        verbose_name_plural = 'Envíos Colaborativos'
        unique_together = [['coop_activity', 'student']]

    def __str__(self):
        return f"Paso {self.step} — {self.student.get_full_name()} → {self.coop_activity.title}"
