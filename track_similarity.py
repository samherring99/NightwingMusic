import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.metrics.pairwise import cosine_similarity

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id='ID', client_secret='SCERET')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to get audio features for a list of track URIs
def get_audio_features(track_uris):
    audio_features = []
    for uri in track_uris:
        analysis = sp.audio_analysis(uri)
        print(analysis)

        ## FIGURE OUT WAYS TO SPLIT THIS UP

        audio_features.extend(analysis)
    return audio_features

# Function to calculate similarity between tracks based on audio features
def calculate_similarity(features1, features2):
    features1 = [f for f in features1[0].values() if isinstance(f, (int, float))]
    features2 = [f for f in features2[0].values() if isinstance(f, (int, float))]
    return cosine_similarity([features1], [features2])[0][0]

# Example track URIs
track_uris = ['7zHOs0OLz4CmB8LHcf1NNv', '4AwJSk491AvHk2AAJReGzZ']

# Get audio features for the tracks
features = get_audio_features(track_uris)

print(features)

# Calculate similarity between the tracks
similarity_score = calculate_similarity(features[:1], features[1:])

print("Similarity score between the tracks:", similarity_score)
