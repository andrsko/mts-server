# Generated by Django 3.1.4 on 2021-01-12 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0006_auto_20210111_2308'),
    ]

    operations = [
        migrations.CreateModel(
            name='YTChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('title', models.CharField(blank=True, max_length=70)),
            ],
        ),
    ]
