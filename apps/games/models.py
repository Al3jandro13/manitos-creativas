from django.db import models
from apps.accounts.models import CustomUser


class PuzzleImage(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='puzzle_images')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='puzzle_images/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imagen de Rompecabezas'
        verbose_name_plural = 'Imágenes de Rompecabezas'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ColoringImage(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='coloring_images')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='coloring_images/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imagen para Colorear'
        verbose_name_plural = 'Imágenes para Colorear'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Game(models.Model):
    TYPE_CHOICES = [
        ('puzzle', '🧩 Rompecabezas'),
        ('coloring', '🖍️ Colorear'),
        ('story', '📖 Cuento'),
        ('consonants', '🔤 Consonantes'),
        ('numbers', '🔢 Números'),
        ('math_add', '➕ Sumas'),
        ('math_sub', '➖ Restas'),
        ('signs', '🤟 Lenguaje de Señas'),
        ('drawing', '🎨 Dibujo Libre'),
        ('snake', '🐍 Serpiente'),
        ('wordsearch', '🔠 Sopa de Letras'),
    ]

    name = models.CharField(max_length=200)
    game_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='games/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    stars_reward = models.PositiveIntegerField(default=3)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Juego'
        verbose_name_plural = 'Juegos'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class GameSession(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='game_sessions')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    stars_earned = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Sesión de Juego'
        verbose_name_plural = 'Sesiones de Juego'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.game.name}"
