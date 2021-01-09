from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
import json, time
from .models import Channel

# get channels info: number, tags
def index(request):
    context = cache.get("channels")
    return HttpResponse(context)


# get current video id and seconds since started
def channel(request, channel_id):
    current_video = json.loads(cache.get(channel_id))
    seconds_since_started = time.time() - current_video["started_at"]
    context = {"id": current_video["id"], "startAt": seconds_since_started}
    return JsonResponse(context)
