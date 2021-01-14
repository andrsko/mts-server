from django.apps import AppConfig
from django.core.cache import cache
import sched, time, json, random, threading, bisect
from . import yt_api

# on server start:
#   recurse schedule for every channel:
#       get channel tags
#       pick randomly one of tags, for this tag pick random video
#       save to redis with current time
#       schedule same procedure in current video duration

s = sched.scheduler(time.time, time.sleep)

# by channel
tags = {}
number_of_tags = {}

# by tag

videos = {}

playlists = {}
playlist_count_sequence = {}

number_of_individual_videos = {}
total_number_of_videos = {}


def get_playlist_video_id(tag, position):
    count_sequence = playlist_count_sequence[tag]

    # find index of leftmost value greater than x
    playlist_index = bisect.bisect_right(count_sequence, position)

    if playlist_index == 0:
        video_index = position
    else:
        video_index = position - count_sequence[playlist_index - 1]

    playlist_id = playlists[tag][playlist_index].get_yt_id()
    return yt_api.get_playlist_video_id(playlist_id, video_index)


def set_current_video(channel):
    # get random tag
    channel_tags = tags[channel]
    random_tag_index = random.randint(0, number_of_tags[channel] - 1)
    random_tag = channel_tags[random_tag_index]

    # get random video
    random_video_duration = 0
    while not random_video_duration:
        random_video_index = random.randint(0, total_number_of_videos[random_tag] - 1)
        if random_video_index < number_of_individual_videos[random_tag]:
            random_video = videos[random_tag][random_video_index]
            random_video_yt_id = random_video.get_yt_id()
        else:
            random_video_yt_id = get_playlist_video_id(random_tag, random_video_index)

        if random_video_yt_id:
            random_video_duration = yt_api.get_video_duration(random_video_yt_id)

    # store current video info in cache
    cache.set(
        channel.id,
        json.dumps({"id": random_video_yt_id, "started_at": time.time()}),
    )

    # store current video duration to check for expiration on server restart
    cache.set(str(channel.id) + "_video_duration", random_video_duration)

    # schedule refreshing
    s.enter(random_video_duration, 1, set_current_video, (channel,))


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
        from .models import Tag, Video, Playlist, Channel

        # get contents

        channels = Channel.objects.all()
        # write channel tags to cache
        tag_names_by_channel = {}
        for channel in channels:
            tags[channel] = channel.tags.all()
            number_of_tags[channel] = len(tags[channel])
            tag_names_by_channel[channel.id] = list(
                tags[channel].values_list("name", flat=True)
            )
        channels_n = len(channels)
        cache.set(
            "channels",
            json.dumps({"n": channels_n, "tags": tag_names_by_channel}),
        )

        # structure data to be used for scheduler
        for tag in Tag.objects.all():
            videos[tag] = Video.objects.filter(tags=tag)

            len_videos_tag = len(videos[tag])
            number_of_individual_videos[tag] = len_videos_tag
            total_number_of_videos[tag] = len_videos_tag

            playlists[tag] = Playlist.objects.filter(tags=tag)
            if len(playlists[tag]):
                playlist_count_sequence[tag] = [
                    number_of_individual_videos[tag]
                    + playlists[tag][0].number_of_videos,
                ]
                for i in range(1, len(playlists[tag])):
                    playlist_count_sequence[tag].append(
                        playlist_count_sequence[tag][-1]
                        + playlists[tag][i].number_of_videos
                    )
                total_number_of_videos[tag] = playlist_count_sequence[tag][-1]

        # start scheduling
        t = threading.Thread(target=set_current, args=(channels,))
        t.setDaemon(True)
        t.start()