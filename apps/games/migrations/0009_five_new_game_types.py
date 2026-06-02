from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0008_three_new_games'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('puzzle',          '🧩 Rompecabezas'),
                    ('coloring',        '🖍️ Colorear'),
                    ('story',           '📖 Cuento'),
                    ('consonants',      '🔤 Consonantes'),
                    ('numbers',         '🔢 Números'),
                    ('math_add',        '➕ Sumas'),
                    ('math_sub',        '➖ Restas'),
                    ('signs',           '🤟 Lenguaje de Señas'),
                    ('drawing',         '🎨 Dibujo Libre'),
                    ('snake',           '🐍 Serpiente'),
                    ('wordsearch',      '🔠 Sopa de Letras'),
                    ('memory',          '🃏 Memoria Visual'),
                    ('counting',        '🔢 Contar Objetos'),
                    ('shapes',          '🔷 Figuras Geométricas'),
                    ('place_value',     '🏠 Unidades, Decenas y Centenas'),
                    ('mixing',          '🎨 Mezcla de Colores'),
                    ('train_syllables', '🚂 Silabas en el Tren'),
                    ('puppet',          '🎭 Marioneta Magica'),
                    ('crazy_face',      '🤪 Cara Loca'),
                    ('rocket',          '🚀 Cohete Explorador'),
                    ('rocket_coop',     '👩‍🚀 Mision Espacial en Pareja'),
                    ('house',           '🏠 Constructor de Casas'),
                    ('shadows',         '🎭 Teatro de Sombras'),
                ],
            ),
        ),
    ]
