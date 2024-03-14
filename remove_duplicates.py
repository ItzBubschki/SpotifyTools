import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

scope = "playlist-modify-private playlist-read-private"
sp = spotipy.Spotify(oauth_manager=SpotifyOAuth(scope=scope))

source_playlist = input("Enter the playlist ID to deduplicate: ")
user_id = sp.me()['id']


# Get all songs from the source playlist (accounting for pagination)
def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


source_tracks = get_playlist_tracks(source_playlist)

# Remove duplicates (using set to automatically ignore duplicates)
song_ids = set()
for track in source_tracks:
    song_ids.add(track['track']['id'])

# Create a new playlist
playlist_name = input("Enter a name for the new playlist: ")
new_playlist = sp.user_playlist_create(user_id, playlist_name, public=False)


# Add songs to the new playlist
# Spotify's `playlist_add_items` can only add 100 songs at a time, so we need to split our list if necessary
def add_songs_to_playlist(playlist_id, song_ids):
    for i in range(0, len(song_ids), 100):
        sp.playlist_add_items(playlist_id, list(song_ids)[i:i + 100])


add_songs_to_playlist(new_playlist['id'], song_ids)

print(f"Deduplicated playlist created: {new_playlist['external_urls']['spotify']}")
