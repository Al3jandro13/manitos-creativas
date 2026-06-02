from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitycategory',
            name='name',
            field=models.CharField(
                choices=[
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
                ],
                max_length=50,
                unique=True,
            ),
        ),
        migrations.RemoveField(
            model_name='activity',
            name='difficulty',
        ),
    ]
