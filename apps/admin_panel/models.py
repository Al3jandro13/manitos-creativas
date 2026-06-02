from django.db import models


class SystemConfig(models.Model):
    is_blocked = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Configuración del Sistema'

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
