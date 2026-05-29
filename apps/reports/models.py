from django.db import models
from apps.accounts.models import CustomUser


class GradeRecord(models.Model):
    PERFORMANCE_CHOICES = [
        ('S', '🌟 Superior'),
        ('A', '😊 Alto'),
        ('B', '🙂 Básico'),
        ('L', '📚 En Proceso'),
    ]
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='grade_records')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_grades')
    subject = models.CharField(max_length=100, verbose_name='Área/Materia')
    period = models.CharField(max_length=50, verbose_name='Período')
    grade = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Nota')
    performance = models.CharField(max_length=2, choices=PERFORMANCE_CHOICES)
    observations = models.TextField(blank=True, verbose_name='Observaciones')
    emotional_progress = models.CharField(max_length=200, blank=True, verbose_name='Progreso emocional')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Plantilla de Notas'

    def __str__(self):
        return f"{self.student.get_full_name()} — {self.subject} — {self.period}"


class WeeklyReport(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='weekly_reports')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_reports')
    week_start = models.DateField(verbose_name='Inicio de semana')
    week_end = models.DateField(verbose_name='Fin de semana')
    creativity_score = models.PositiveSmallIntegerField(default=5, verbose_name='Creatividad')
    behavior_score = models.PositiveSmallIntegerField(default=5, verbose_name='Comportamiento')
    progress_score = models.PositiveSmallIntegerField(default=5, verbose_name='Progreso')
    participation_score = models.PositiveSmallIntegerField(default=5, verbose_name='Participación')
    attendance_score = models.PositiveSmallIntegerField(default=5, verbose_name='Asistencia')
    observations = models.TextField(blank=True)
    achievements = models.TextField(blank=True, verbose_name='Logros')
    recommendations = models.TextField(blank=True, verbose_name='Recomendaciones')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reporte Semanal'
        verbose_name_plural = 'Reportes Semanales'
        ordering = ['-week_start']

    def __str__(self):
        return f"{self.student.get_full_name()} — Semana {self.week_start}"

    @property
    def average_score(self):
        scores = [
            self.creativity_score, self.behavior_score,
            self.progress_score, self.participation_score, self.attendance_score
        ]
        return round(sum(scores) / len(scores), 1)
