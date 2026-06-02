from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0005_coop_puzzle_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitycategory',
            name='name',
            field=models.CharField(
                max_length=50,
                unique=True,
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
                    ('memoria', '🃏 Memoria Visual'),
                    ('contar_objetos', '🔢 Contar Objetos'),
                    ('figuras', '🔷 Figuras Geométricas'),
                    ('sopa_letras_coop', '🔠 Sopa de Letras en Pareja'),
                    ('cuento_coop', '📖 Cuento en Pareja'),
                    ('mural_coop', '🖼️ Mural Colaborativo'),
                ],
            ),
        ),
    ]
