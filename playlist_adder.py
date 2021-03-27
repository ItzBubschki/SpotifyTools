import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

scope = "playlist-modify-private playlist-read-private"

sp = spotipy.Spotify(oauth_manager=SpotifyOAuth(scope=scope))


source_playlist = input("Enter the playlist to add the songs from: ")
target_playlist = input("Enter the playlist to add the songs into: ")

try:
    source = sp.playlist(source_playlist)
    source_songs = source['tracks']['items']
    song_ids = []
    for song in source_songs:
        song_ids.append(song['track']['id'])
    sp.playlist_add_items(target_playlist, song_ids)
except Exception:
    print("Invalid source or target. Quitting!")
    quit()