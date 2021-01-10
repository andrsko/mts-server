import os, re, json
import urllib.request
import urllib.parse

API_KEY = os.environ.get("YT_API_KEY")


def _fetch_json(url, params):
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_contents = response.read()
        data = json.loads(response_contents.decode())

    return data


def _get_video_data(id, part):
    params = {"id": id, "key": API_KEY, "part": part}
    api_url = "https://youtube.googleapis.com/youtube/v3/videos"
    data = _fetch_json(api_url, params)
    if data["items"] != []:
        return data
    else:
        return None


def get_video_duration(id):
    data = _get_video_data(id, "contentDetails")
    if data:
        return _YTDurationToSeconds(data["items"][0]["contentDetails"]["duration"])
    else:
        return 0


def _YTDurationToSeconds(duration):
    match = re.match("PT(\d+H)?(\d+M)?(\d+S)?", duration).groups()
    hours = int(match[0][:-1]) if match[0] else 0
    minutes = int(match[1][:-1]) if match[1] else 0
    seconds = int(match[2][:-1]) if match[2] else 0
    return hours * 3600 + minutes * 60 + seconds


def get_video_title(id):
    data = _get_video_data(id, "snippet")
    if data:
        return data["items"][0]["snippet"]["title"]
    else:
        return "Not Found"
