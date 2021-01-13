from django.contrib import admin

from .models import Tag, YTChannel, Video, Channel


class VideoAdmin(admin.ModelAdmin):
    list_filter = ("yt_channel", "tags")


class ChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "get_tags")

    def get_tags(self, obj):
        return ", ".join([t.name for t in obj.tags.all()])

    get_tags.short_description = "Tags"


admin.site.register(Tag)
admin.site.register(YTChannel)
admin.site.register(Video, VideoAdmin)
admin.site.register(Channel, ChannelAdmin)
