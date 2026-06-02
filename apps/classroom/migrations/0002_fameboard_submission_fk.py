from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_remove_difficulty_update_categories'),
        ('classroom', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fameboardentry',
            name='submission',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='fame_entries',
                to='activities.activitysubmission',
            ),
        ),
        migrations.AlterField(
            model_name='fameboardentry',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
