# Generated by Django 4.2.2 on 2023-07-05 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zob_posts', '0006_collabpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='collaboration',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zob_posts.post'),
        ),
        migrations.DeleteModel(
            name='CollabPost',
        ),
    ]
