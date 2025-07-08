import lyricsgenius
import os

genius_token = os.getenv("GENIUS_TOKEN")

if not genius_token:
    raise RuntimeError("GENIUS_TOKEN chưa được đặt trong biến môi trường")

genius = lyricsgenius.Genius(genius_token)

def get_lyrics(title):
    song = genius.search_song(title)
    if song:
        return song.lyrics
    return None