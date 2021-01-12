from django.db.models import Model, URLField, IntegerField, ManyToManyField, CharField

from . import yt_api


class Tag(Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name


class Video(Model):
    url = URLField(unique=True)
    tags = ManyToManyField(Tag)
    title = CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # fetch video title with YT API
        self.title = yt_api.get_video_title(self.get_yt_id())
        super().save(*args, **kwargs)

    def get_yt_id(self):
        return self.url[-11:]


class Channel(Model):
    tags = ManyToManyField(Tag)
