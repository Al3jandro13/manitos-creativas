import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_coop_activity'),
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coopactivity',
            name='coloring_image',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='coop_activities',
                to='games.coloringimage',
            ),
        ),
    ]
