import os
import re
from googleapiclient.discovery import build

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise ValueError("⚠️ Missing YOUTUBE_API_KEY environment variable")

def is_youtube_url(url):
    return "youtube.com" in url or "youtu.be" in url

def search_youtube(query, max_results=10):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        search_response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results
        ).execute()

        results = []
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            results.append({
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "title": title
            })
        return results
    
    except Exception as e:
        print(f"[ERROR] search_youtube: {e}")
        return []

def get_playlist_videos(playlist_url):
    match = re.search(r"list=([a-zA-Z0-9_-]+)", playlist_url)
    if not match:
        print(f"[WARN] Không tìm thấy playlist ID trong URL: {playlist_url}")
        return []

    playlist_id = match.group(1)

    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        videos = []
        nextPageToken = None
        while True:
            pl_request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=nextPageToken
            )
            pl_response = pl_request.execute()
            for item in pl_response["items"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                title = item["snippet"]["title"]
                videos.append({
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "title": title
                })
            nextPageToken = pl_response.get("nextPageToken")
            if not nextPageToken:
                break
        return videos
    
    except Exception as e:
        print(f"[ERROR] get_playlist_videos: {e}")
        return []
