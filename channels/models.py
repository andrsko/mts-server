from django.db.models import Model, URLField, IntegerField, ManyToManyField, CharField


class Tag(Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name


class Video(Model):
    url = URLField()
    tags = ManyToManyField(Tag)

    def __str__(self):
        return self.url


class Channel(Model):
    tags = ManyToManyField(Tag)
