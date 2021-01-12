from django.contrib import admin

from .models import Tag, YTChannel, Video, Channel


class VideoAdmin(admin.ModelAdmin):
    list_filter = ("yt_channel", "tags")


admin.site.register(Tag)
admin.site.register(YTChannel)
admin.site.register(Video, VideoAdmin)
admin.site.register(Channel)
