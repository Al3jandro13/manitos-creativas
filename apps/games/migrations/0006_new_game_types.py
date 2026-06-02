from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_add_wordsearch_game_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_type',
            field=models.CharField(
                max_length=20,
                choices=[
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
                    ('memory', '🃏 Memoria Visual'),
                    ('counting', '🔢 Contar Objetos'),
                    ('shapes', '🔷 Figuras Geométricas'),
                ],
            ),
        ),
    ]
