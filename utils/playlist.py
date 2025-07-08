import json
import os

PLAYLIST_DIR = "playlists"

def save_user_playlist_link(user_id: int, name: str, url: str):
    os.makedirs(PLAYLIST_DIR, exist_ok=True)
    path = os.path.join(PLAYLIST_DIR, f"{user_id}.json")
    data = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[name] = url
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_user_playlist_link(user_id: int, name: str):
    path = os.path.join(PLAYLIST_DIR, f"{user_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(name)
