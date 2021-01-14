# Generated by Django 3.1.4 on 2021-01-14 21:06

from django.db import migrations

from channels.yt_api import is_video_embeddable


def delete_not_embeddable_videos(apps, schema_editor):
    Video = apps.get_model("channels", "Video")
    YTChannel = apps.get_model("channels", "YTChannel")

    for video in Video.objects.all():
        yt_channel = video.yt_channel
        if not is_video_embeddable(video.url[-11:]):
            video.delete()
            if not yt_channel.video_set.all().exists():
                yt_channel.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("channels", "0012_playlist_number_of_videos"),
    ]

    operations = [
        migrations.RunPython(delete_not_embeddable_videos),
    ]
