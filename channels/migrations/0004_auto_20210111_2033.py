# Generated by Django 3.1.4 on 2021-01-11 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0003_remove_video_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='url',
            field=models.URLField(unique=True),
        ),
    ]
