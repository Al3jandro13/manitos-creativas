import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0004_coop_coloring_image'),
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coopactivity',
            name='puzzle_image',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='coop_activities',
                to='games.puzzleimage',
            ),
        ),
        migrations.AddField(
            model_name='coopactivity',
            name='puzzle_rows',
            field=models.PositiveSmallIntegerField(default=2),
        ),
        migrations.AddField(
            model_name='coopactivity',
            name='puzzle_cols',
            field=models.PositiveSmallIntegerField(default=4),
        ),
    ]
