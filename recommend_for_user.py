import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
import time

# Spotify API credentials
CLIENT_ID = 'XXXXXXXX'
CLIENT_SECRET = 'XXXXXXXX'

# Initialize Spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_user_playlists(username):
    """Get a user's public playlists"""
    playlists = sp.user_playlists(username)
    return [playlist['id'] for playlist in playlists['items']]

def get_playlist_tracks(playlist_id):
    """Get tracks from a playlist"""
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append(track['id'])
    return tracks

def recommend_tracks(username):
    """Recommend tracks not in the user's playlists"""
    user_playlists = get_user_playlists(username)
    all_playlist_tracks = []
    for playlist_id in user_playlists:
        all_playlist_tracks.extend(get_playlist_tracks(playlist_id))
        time.sleep(1)

    recommendations = sp.recommendations(seed_tracks=all_playlist_tracks[:5], limit=20)
    recommended_tracks = [track['id'] for track in recommendations['tracks']]

    recommended_tracks = [track for track in recommended_tracks if track not in all_playlist_tracks]

    return recommended_tracks[:10]

if __name__ == "__main__":
    username = 'username'
    recommended_tracks = recommend_tracks(username)
    print("Recommended Tracks:")
    for i, track_id in enumerate(recommended_tracks, 1):
        track_info = sp.track(track_id)
        print(f"{i}. {track_info['name']} by {', '.join(artist['name'] for artist in track_info['artists'])}")
