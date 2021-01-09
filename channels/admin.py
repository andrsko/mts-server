from django.contrib import admin

from .models import Tag, Video, Channel

admin.site.register(Tag)
admin.site.register(Video)
admin.site.register(Channel)
