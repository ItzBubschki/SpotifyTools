import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import requests
from io import BytesIO

load_dotenv()

scope = "playlist-modify-private playlist-read-private ugc-image-upload"

sp = spotipy.Spotify(oauth_manager=SpotifyOAuth(scope=scope))


def get_all_artist_songs(artist_id):
    """Fetch all songs from an artist, removing duplicates."""
    all_songs = dict()  # Use dict to track unique song IDs and their release dates
    album_types = ['album', 'single', 'compilation', 'appears_on']
    albums = []
    for album_type in album_types:
        results = sp.artist_albums(artist_id, include_groups=album_type)
        albums.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            albums.extend(results['items'])
    print(f"Found {len(albums)} albums/singles/EPs/compilations")

    # Get all tracks from all albums
    for album in albums:
        album_release_date = album.get('release_date', '')
        results = sp.album_tracks(album['id'])
        tracks = results['items']

        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        for track in tracks:
            # Check if the artist is the main artist (first in the list)
            if track['artists'] and track['artists'][0]['id'] == artist_id:
                # Use album release date for sorting
                all_songs[track['id']] = album_release_date

    # Sort song IDs by release date (oldest to newest)
    sorted_songs = sorted(all_songs.items(), key=lambda x: x[1] or '')
    return [song_id for song_id, _ in sorted_songs]


def get_artist_image(artist_id):
    """Get the artist's image URL."""
    artist = sp.artist(artist_id)
    if artist['images'] and len(artist['images']) > 0:
        return artist['images'][0]['url']
    return None


def convert_image_to_base64(image_url):
    """Convert image URL to base64 string for Spotify API."""
    if not image_url:
        return None
    
    try:
        response = requests.get(image_url)
        image_data = response.content
        import base64
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"Could not convert image: {e}")
        return None


def search_artist(artist_name):
    """Search for an artist and return their ID."""
    results = sp.search(q=artist_name, type='artist', limit=5)
    
    if not results['artists']['items']:
        print("No artists found!")
        return None
    
    print("\nTop 5 artists matching your search:")
    for i, artist in enumerate(results['artists']['items'], 1):
        print(f"{i}. {artist['name']} (Popularity: {artist['popularity']})")
    
    choice = input("\nSelect the artist (enter number): ")
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(results['artists']['items']):
            return results['artists']['items'][choice_idx]['id']
    except ValueError:
        pass
    
    print("Invalid selection!")
    return None


def get_user_playlists():
    """Get all private playlists owned by the user."""
    playlists = []
    results = sp.current_user_playlists(limit=50)
    
    while results:
        for item in results['items']:
            if item['owner']['id'] == sp.current_user()['id']:
                playlists.append((item['id'], item['name']))
        
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    return playlists


def add_songs_to_playlist(playlist_id, song_ids):
    """Add songs to a playlist in batches (Spotify API limit is 100)."""
    batch_size = 100
    for i in range(0, len(song_ids), batch_size):
        batch = song_ids[i:i + batch_size]
        sp.playlist_add_items(playlist_id, batch)
        print(f"Added {len(batch)} songs to playlist")


def main():
    # Get artist
    artist_name = input("Enter the artist name: ")
    artist_id = search_artist(artist_name)
    
    if not artist_id:
        return
    
    artist = sp.artist(artist_id)
    artist_name = artist['name']
    
    print(f"\nFetching all songs from {artist_name}...")
    song_ids = get_all_artist_songs(artist_id)
    print(f"Found {len(song_ids)} unique songs")

    # Ask user about playlist
    user_playlists = get_user_playlists()
    
    if user_playlists:
        print("\nYour playlists:")
        for i, (_, name) in enumerate(user_playlists, 1):
            print(f"{i}. {name}")
        print(f"{len(user_playlists) + 1}. Create a new playlist")
        
        choice = input("\nSelect a playlist or create new (enter number): ")
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(user_playlists):
                playlist_id = user_playlists[choice_idx][0]
                print(f"Adding songs to existing playlist...")
            else:
                playlist_id = None
                print("Creating new playlist")
        except ValueError:
            playlist_id = None
            print("Creating new playlist")
    else:
        choice = input("No playlists found. Create a new one? (y/n): ")
        if choice.lower() != 'y':
            print("Aborted.")
            return
        playlist_id = None
    
    # Create new playlist if needed
    if playlist_id is None:
        playlist_name = f"All of {artist_name}"
        user = sp.current_user()
        playlist = sp.user_playlist_create(user['id'], playlist_name, public=False)
        playlist_id = playlist['id']
        print(f"Created new playlist: {playlist_name}")
        
        # Set playlist image
        artist_image_url = get_artist_image(artist_id)
        if artist_image_url:
            image_base64 = convert_image_to_base64(artist_image_url)
            if image_base64:
                try:
                    sp.playlist_upload_cover_image(playlist_id, image_base64)
                    print("Set artist image as playlist cover")
                except Exception as e:
                    print(f"Could not set playlist image: {e}")
    
    # Add songs to playlist
    add_songs_to_playlist(playlist_id, song_ids)
    print(f"\nCompleted! Added {len(song_ids)} unique songs to the playlist.")


if __name__ == "__main__":
    main()
