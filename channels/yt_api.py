import os, re, json
import urllib.request
import urllib.parse


def get_video_duration(video_id):
    API_KEY = os.environ.get("YT_API_KEY")
    params = {"id": video_id, "key": API_KEY, "part": "contentDetails"}
    api_url = "https://youtube.googleapis.com/youtube/v3/videos"

    query_string = urllib.parse.urlencode(params)
    api_video_url = api_url + "?" + query_string

    with urllib.request.urlopen(api_video_url) as response:
        response_contents = response.read()
        data = json.loads(response_contents.decode())

    duration = 0
    if data["items"] != []:
        duration = _YTDurationToSeconds(data["items"][0]["contentDetails"]["duration"])

    return duration


def _YTDurationToSeconds(duration):
    match = re.match("PT(\d+H)?(\d+M)?(\d+S)?", duration).groups()
    hours = int(match[0][:-1]) if match[0] else 0
    minutes = int(match[1][:-1]) if match[1] else 0
    seconds = int(match[2][:-1]) if match[2] else 0
    return hours * 3600 + minutes * 60 + seconds