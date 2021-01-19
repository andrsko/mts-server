from django.db.models import (
    Model,
    URLField,
    IntegerField,
    ManyToManyField,
    CharField,
    ForeignKey,
    CASCADE,
)
from django.core.exceptions import ValidationError

from . import yt_api

from urllib import parse


class Tag(Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name


class YTChannel(Model):
    url = URLField(unique=True)
    title = CharField(max_length=70, blank=True)

    def __str__(self):
        return self.title


class Video(Model):
    url = URLField(unique=True)
    tags = ManyToManyField(Tag)
    title = CharField(max_length=100, blank=True)
    yt_channel = ForeignKey(YTChannel, on_delete=CASCADE, blank=True)

    def __str__(self):
        return self.title

    def clean(self):
        if not yt_api.is_video_embeddable(self.get_yt_id()):
            raise ValidationError("Video must be embeddable.")

    def save(self, *args, **kwargs):
        # fetch video info with YT API
        self.title = yt_api.get_video_title(self.get_yt_id())
        yt_channel_data = yt_api.get_video_channel(self.get_yt_id())

        # assign yt channel
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

        self.yt_channel = yt_channel

        super().save(*args, **kwargs)

    def get_yt_id(self):
        return self.url[-11:]


class Playlist(Model):
    url = URLField(unique=True)
    tags = ManyToManyField(Tag)
    title = CharField(max_length=100, blank=True)
    number_of_videos = IntegerField(default=0, blank=True)
    yt_channel = ForeignKey(YTChannel, on_delete=CASCADE, blank=True)

    def __str__(self):
        return self.title

    def clean(self):
        first_video_id = yt_api.get_playlist_video_id(self.get_yt_id(), 0)
        if not yt_api.is_video_embeddable(first_video_id):
            raise ValidationError("Playlist videos must be embeddable.")

    def save(self, *args, **kwargs):
        # fetch playlist info with YT API
        self.title = yt_api.get_playlist_title(self.get_yt_id())
        self.number_of_videos = yt_api.get_playlist_item_count(self.get_yt_id())
        yt_channel_data = yt_api.get_playlist_channel(self.get_yt_id())

        # assign yt channel
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

        self.yt_channel = yt_channel

        super().save(*args, **kwargs)

    def get_yt_id(self):
        return parse.parse_qs(parse.urlsplit(self.url).query)["list"][0]


class Channel(Model):
    title = CharField(max_length=50)
    tags = ManyToManyField(Tag)
