import sys
import datetime
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from dotenv import load_dotenv
import os

load_dotenv()

REFRESH_TOKEN = os.environ. get('SPOTIPY_REFRESH_TOKEN')

if not REFRESH_TOKEN:
    raise Exception('Missing required environment variable: SPOTIPY_REFRESH_TOKEN')

oauth = SpotifyOAuth(scope='playlist-modify-public playlist-modify-private')

# Manually set the refresh token and get a valid access token
token_info = oauth.refresh_access_token(REFRESH_TOKEN)
access_token = token_info['access_token']
sp = spotipy.Spotify(auth=access_token)

def get_recent_tracks(artist_id):
    one_week_ago = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)).date()
    albums = []
    album_types = ['album', 'single', 'compilation', 'appears_on']
    for album_type in album_types:
        results = sp.artist_albums(artist_id, include_groups=album_type, limit=50)
        albums.extend(results["items"])
        while results["next"]:
            results = sp.next(results)
            albums.extend(results["items"])
    recent_tracks = set()
    for album in albums:
        release_date = album.get("release_date")
        if not release_date:
            continue
        # Handle different date precisions
        if len(release_date) == 4:
            continue  # year only
        elif len(release_date) == 7:
            continue  # year-month only
        album_date = datetime.datetime.strptime(release_date, "%Y-%m-%d").date()
        if album_date >= one_week_ago:
            # Get tracks for this album
            tracks = sp.album_tracks(album["id"])["items"]
            for track in tracks:
                if track['artists'] and track['artists'][0]['id'] == artist_id:
                    recent_tracks.add(track["id"])
    return list(recent_tracks)

def get_playlist_track_ids(playlist_id):
    track_ids = set()
    results = sp.playlist_tracks(playlist_id, fields="items.track.id,next", additional_types=["track"])
    while True:
        for item in results["items"]:
            track = item.get("track")
            if track:
                track_ids.add(track["id"])
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return track_ids

def add_tracks_to_playlist(playlist_id, track_ids):
    if not track_ids:
        return
    uris = [f"spotify:track:{tid}" for tid in track_ids]
    batch_size = 100
    for i in range(0, len(uris), batch_size):
        batch = uris[i:i+batch_size]
        sp.playlist_add_items(playlist_id, batch)
    print(f"Added {len(track_ids)} tracks to playlist {playlist_id}.")

def main():
    if len(sys.argv) < 3:
        raise Exception("Usage: python sync_artist_recent_to_playlist.py <artist_id> <playlist_id>")
    artist_id = sys.argv[1]
    playlist_id = sys.argv[2]
    print(f"Checking for recent releases for artist {artist_id}...")
    recent_tracks = get_recent_tracks(artist_id)
    if not recent_tracks:
        print("No new releases in the last week.")
        return
    print(f"Found {len(recent_tracks)} recent tracks. Checking playlist...")
    playlist_tracks = get_playlist_track_ids(playlist_id)
    to_add = [tid for tid in recent_tracks if tid not in playlist_tracks]
    if not to_add:
        print("All recent tracks are already in the playlist.")
        return
    print(f"Adding {len(to_add)} new tracks to playlist...")
    add_tracks_to_playlist(playlist_id, to_add)

if __name__ == "__main__":
    main()
