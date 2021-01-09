from django.apps import AppConfig
from django.core.cache import cache
import sched, time, json, random, threading

# on server start:
#   recurse schedule for every channel:
#       get channel tags
#       pick randomly one of tags, for this tag pick random video
#       save to redis with current time
#       schedule same procedure in current video duration

s = sched.scheduler(time.time, time.sleep)

tags_by_channel = {}
videos_by_tag = {}


def set_current_video(channel):
    # get random tag
    channel_tags = tags_by_channel[channel]
    random_tag_index = random.randint(0, channel_tags.count() - 1)
    random_tag = channel_tags[random_tag_index]

    # get random video
    random_video_index = random.randint(0, videos_by_tag[random_tag].count() - 1)
    random_video = videos_by_tag[random_tag][random_video_index]

    # store current video info in cache
    cache.set(
        channel.id,
        json.dumps({"id": random_video.url[-11:], "started_at": time.time()}),
    )

    # store current video duration to check for expiration on server restart
    cache.set(str(channel.id) + "_video_duration", random_video.duration)

    # schedule refreshing
    s.enter(random_video.duration, 1, set_current_video, (channel,))


# set current videos, schedule refreshing
def set_current(channels):
    for channel in channels:
        channel_cache_json = cache.get(channel.id, "not set")
        video_duration_cache = cache.get(str(channel.id) + "_video_duration", "not set")

        if channel_cache_json != "not set" and video_duration_cache != "not set":
            channel_cache = json.loads(channel_cache_json)

            # cache has been set before server restart
            # pick up scheduling where it was interrupted
            time_passed = time.time() - channel_cache["started_at"]
            if time_passed >= video_duration_cache:
                # video has finished streaming, pick new and set scheduler
                set_current_video(channel)
            else:
                # pick up where it is supposed to be at this moment
                s.enter(
                    video_duration_cache - time_passed, 1, set_current_video, (channel,)
                )
        # cache and scheduling hasn't been initizialized yet
        else:
            set_current_video(channel)

    s.run()


class ChannelsConfig(AppConfig):
    name = "channels"

    def ready(self):
        from .models import Tag, Video, Channel

        tags = Tag.objects.all()
        channels = Channel.objects.all()

        tag_names_by_channel = {}
        for channel in channels:
            tags_by_channel[channel] = channel.tags.all()
            tag_names_by_channel[channel.id] = list(
                channel.tags.all().values_list("name", flat=True)
            )
        channels_n = channels.count()
        cache.set(
            "channels",
            json.dumps({"n": channels_n, "tags": tag_names_by_channel}),
        )

        for tag in tags:
            videos_by_tag[tag] = Video.objects.filter(tags=tag)

        t = threading.Thread(target=set_current, args=(channels,))
        t.setDaemon(True)
        t.start()