import time
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import difflib

def song_play(_query):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.environ.get("SPOTIPY_ID"),
        client_secret=os.environ.get("SPOTIPY_SECRET"),
        redirect_uri="http://localhost:8080",
        scope="user-modify-playback-state user-read-playback-state "
    ))

    def wait_for_device():
        print("Waiting for Spotify to become active...")
        for _ in range(10):
            devices = sp.devices()
            device_list = devices.get('devices', [])

            if device_list:

                for device in device_list:
                    print(f"Active Device Found: {device['name']}")
                    return device['id']

            time.sleep(10)

        print("No active device found. Make sure Spotify is running and logged in.")
        return None

    def play_song(_query):

        os.startfile(os.environ.get("SPOTIFY_PATH"))

        device_id = wait_for_device()
        if not device_id:
            return
        normalized_query = _query.lower().strip()
        liked_song_commands = ["liked songs", "play my library", "play my liked songs", "play liked"]
        if normalized_query in liked_song_commands:
            try:
                user_id = sp.me()['id']
                
                liked_songs_uri = f"spotify:user:{user_id}:collection"
                        
                sp.shuffle(True, device_id=device_id)
                        
                sp.start_playback(device_id=device_id, context_uri=liked_songs_uri)
                print("Playing your liked songs on shuffle.")
            except Exception as e:
                print(f"Could not play liked songs: {e}")
        results = sp.search(q=_query, type="track", limit=10)
        tracks = results.get('tracks', {}).get('items', [])

        if tracks:
            sorted_tracks = sorted(
                tracks,
                key=lambda t: (
                    difflib.SequenceMatcher(None, _query.lower(), t['name'].lower()).ratio(),
                    t['popularity']
                ),
                reverse=True
            )
            track = sorted_tracks[0]
            track_name = track['name']
            track_artist = ", ".join(artist['name'] for artist in track['artists'])
            track_id = track['id']

            print(f"Found Track: {track_name} by {track_artist}")
            sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
            print(f"Playing {track_name} by {track_artist}")
        else:
            print(f"No track found for '{_query}'.")

    play_song(_query)
