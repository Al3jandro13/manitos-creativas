from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_delete_graderecord_weeklyreport'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_type', models.CharField(
                    choices=[
                        ('circular', 'Circular'),
                        ('comunicado', 'Comunicado'),
                        ('informe', 'Informe de Seguimiento'),
                        ('citacion', 'Citación'),
                        ('carta', 'Carta a Padres de Familia'),
                    ],
                    default='circular',
                    max_length=30,
                )),
                ('title', models.CharField(max_length=200)),
                ('doc_number', models.CharField(blank=True, max_length=20, verbose_name='Número de documento')),
                ('recipient', models.CharField(blank=True, max_length=200, verbose_name='Dirigido a')),
                ('content', models.TextField(verbose_name='Contenido del documento')),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='documentos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('teacher', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='generated_documents',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Documento Generado',
                'verbose_name_plural': 'Documentos Generados',
                'ordering': ['-created_at'],
            },
        ),
    ]
