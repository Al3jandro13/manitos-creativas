from django.db import models
from django.conf import settings


class GeneratedDocument(models.Model):
    DOCUMENT_TYPES = [
        ('circular', 'Circular'),
        ('comunicado', 'Comunicado'),
        ('informe', 'Informe de Seguimiento'),
        ('citacion', 'Citación'),
        ('carta', 'Carta a Padres de Familia'),
    ]

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_documents',
    )
    doc_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES, default='circular')
    title = models.CharField(max_length=200)
    doc_number = models.CharField(max_length=20, blank=True, verbose_name='Número de documento')
    recipient = models.CharField(max_length=200, blank=True, verbose_name='Dirigido a')
    content = models.TextField(verbose_name='Contenido del documento')
    pdf_file = models.FileField(upload_to='documentos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Documento Generado'
        verbose_name_plural = 'Documentos Generados'

    def __str__(self):
        return f"{self.get_doc_type_display()} {self.doc_number} — {self.title}"

    def delete_pdf(self):
        if self.pdf_file:
            import os
            if os.path.isfile(self.pdf_file.path):
                os.remove(self.pdf_file.path)
            self.pdf_file = None
            self.save()
