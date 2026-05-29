from django.db import models
from apps.accounts.models import CustomUser


class Announcement(models.Model):
    TYPE_CHOICES = [
        ('info', '💬 Información'),
        ('reminder', '⏰ Recordatorio'),
        ('important', '🔴 Importante'),
        ('celebration', '🎉 Celebración'),
    ]
    title = models.CharField(max_length=200, verbose_name='Título')
    message = models.TextField(verbose_name='Mensaje')
    announcement_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='announcements')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FameBoardEntry(models.Model):
    MEDAL_CHOICES = [
        ('gold', '🥇 Oro'),
        ('silver', '🥈 Plata'),
        ('bronze', '🥉 Bronce'),
        ('star', '⭐ Estrella'),
        ('heart', '❤️ Corazón'),
        ('rainbow', '🌈 Arcoíris'),
    ]
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='fame_entries')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='fame_given')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='fame_board/', blank=True, null=True)
    medal_type = models.CharField(max_length=20, choices=MEDAL_CHOICES, default='star')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Salón de la Fama'
        verbose_name_plural = 'Entradas — Salón de la Fama'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.get_full_name()} — {self.title}"
