# Generated by Django 4.2.2 on 2023-07-10 05:42

from django.db import migrations, models
import zob_posts.models


class Migration(migrations.Migration):

    dependencies = [
        ('zob_posts', '0007_post_collaboration_delete_collabpost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='audio_file',
            field=models.FileField(upload_to=zob_posts.models.generate_unique_filename),
        ),
    ]
