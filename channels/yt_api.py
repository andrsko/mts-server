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


def _get_data(
    entity,
    id,
    part,
    id_name="id",
    max_results=1,
):
    api_url = "https://youtube.googleapis.com/youtube/v3/" + entity
    params = {id_name: id, "key": API_KEY, "part": part, "maxResults": max_results}
    data = _fetch_json(api_url, params)
    if data["items"] != []:
        return data
    else:
        return None


def get_video_duration(id):
    data = _get_data("videos", id, "contentDetails")
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
    data = _get_data("videos", id, "snippet")
    if data:
        return data["items"][0]["snippet"]["title"]
    else:
        return "Not Found"


def get_video_channel(id):
    data = _get_data("videos", id, "snippet")
    if data:
        snippet = data["items"][0]["snippet"]
        return {"id": snippet["channelId"], "title": snippet["channelTitle"]}
    else:
        return None


def get_playlist_title(id):
    data = _get_data("playlists", id, "snippet")
    if data:
        return data["items"][0]["snippet"]["title"]
    else:
        return "Not Found"


def get_playlist_channel(id):
    data = _get_data("playlists", id, "snippet")
    if data:
        snippet = data["items"][0]["snippet"]
        return {"id": snippet["channelId"], "title": snippet["channelTitle"]}
    else:
        return None


def get_playlist_item_count(id):
    data = _get_data("playlists", id, "contentDetails")
    if data:
        return data["items"][0]["contentDetails"]["itemCount"]
    else:
        return 0


def _get_playlist_items_next_page_token(id, page_token):
    api_url = "https://youtube.googleapis.com/youtube/v3/playlistItems"
    params = {
        "playlistId": id,
        "key": API_KEY,
        "part": "contentDetails",
        "maxResults": 50,
        "pageToken": page_token,
    }
    data = _fetch_json(api_url, params)
    return data["nextPageToken"]


def _get_playlist_target_video_id(id, page_token, video_index_rel_to_page):
    api_url = "https://youtube.googleapis.com/youtube/v3/playlistItems"
    params = {
        "playlistId": id,
        "key": API_KEY,
        "part": "contentDetails",
        "maxResults": video_index_rel_to_page,
        "pageToken": page_token,
    }
    data = _fetch_json(api_url, params)
    return data["items"][-1]["contentDetails"]["videoId"]


def get_playlist_video_id(playlist_id, video_index):
    data = _get_data("playlistItems", playlist_id, "contentDetails", "playlistId")

    if data and video_index < data["pageInfo"]["totalResults"]:
        n_pages_to_skip, target_page_maxr = divmod(video_index + 1, 50)
        page_token = ""

        for i in range(n_pages_to_skip):
            page_token = _get_playlist_items_next_page_token(playlist_id, page_token)

        return _get_playlist_target_video_id(playlist_id, page_token, target_page_maxr)
    else:
        return None
