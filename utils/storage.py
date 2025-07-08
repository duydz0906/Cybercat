import json
import os

QUEUE_FILE = "queue.json"

def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_queue(queues):
    data = {}
    for guild_id, songs in queues.items():
        data[str(guild_id)] = [
            {"url": s.url, "title": s.title, "duration": s.duration} for s in songs
        ]
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
