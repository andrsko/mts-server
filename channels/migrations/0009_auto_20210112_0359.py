# Generated by Django 3.1.4 on 2021-01-12 01:59

from django.db import migrations

from channels.yt_api import get_video_channel


def populate_yt_channels(apps, schema_editor):
    Video = apps.get_model("channels", "Video")
    YTChannel = apps.get_model("channels", "YTChannel")

    for video in Video.objects.all():
        yt_channel_data = get_video_channel(video.url[-11:])
        if yt_channel_data:
            yt_channel_url = "https://www.youtube.com/channel/" + yt_channel_data["id"]
            yt_channel_title = yt_channel_data["title"]
        else:
            yt_channel_url = "https://www.youtube.com"
            yt_channel_title = "Not Found"

        try:
            yt_channel = YTChannel.objects.get(url=yt_channel_url)
        except YTChannel.DoesNotExist:
            yt_channel = YTChannel.objects.create(
                url=yt_channel_url, title=yt_channel_title
            )

        video.yt_channel = yt_channel
        video.save()


class Migration(migrations.Migration):

    dependencies = [
        ("channels", "0008_video_yt_channel"),
    ]

    operations = [
        migrations.RunPython(populate_yt_channels),
    ]
