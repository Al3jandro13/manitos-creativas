import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_remove_difficulty_update_categories'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CoopActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('instructions', models.TextField(blank=True)),
                ('reward_stars', models.PositiveIntegerField(default=5)),
                ('status', models.CharField(
                    choices=[('draft', 'Borrador'), ('published', 'Publicada'), ('archived', 'Archivada')],
                    default='published',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='activities.activitycategory',
                )),
                ('teacher', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='coop_activities',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('student1', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='coop_as_student1',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('student2', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='coop_as_student2',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Actividad en Pareja',
                'verbose_name_plural': 'Actividades en Parejas',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CoopSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step', models.PositiveSmallIntegerField(choices=[(1, 'Parte 1'), (2, 'Parte 2')])),
                ('drawing_data', models.TextField(blank=True)),
                ('content', models.TextField(blank=True)),
                ('status', models.CharField(
                    choices=[
                        ('waiting', 'Esperando'),
                        ('in_progress', 'En progreso'),
                        ('submitted', 'Enviado'),
                        ('reviewed', 'Revisado'),
                        ('approved', 'Aprobado'),
                    ],
                    default='waiting',
                    max_length=20,
                )),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('teacher_feedback', models.TextField(blank=True)),
                ('stars_awarded', models.PositiveIntegerField(default=0)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('coop_activity', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='submissions',
                    to='activities.coopactivity',
                )),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='coop_submissions',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Envío Colaborativo',
                'verbose_name_plural': 'Envíos Colaborativos',
                'unique_together': {('coop_activity', 'student')},
            },
        ),
    ]
