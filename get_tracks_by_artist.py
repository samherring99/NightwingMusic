import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import os

# Replace with your own credentials
client_id = 'xxxxxxxxx'
client_secret = 'xxxxxxxxx'

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_tracks_for_artist(artist_name):
    results = sp.search(q='artist:' + artist_name, type='track', limit=50)
    return results

response = get_tracks_for_artist("Kanye West")

track_ids = []
results = []

for track in response['tracks']['items']:
    track_ids.append(track['id'])

for track_id in track_ids:
    codestring = sp.audio_analysis(track_id)['track']['codestring']
    entry = {'text': codestring}
    results.append(entry)

with open("track_codes.txt", "w") as file:
    for result in results:
        file.write(result['text'] + "\n\n")
    #writer = csv.DictWriter(csvfile, fieldnames=fields)
    #writer.writeheader()
    #writer.writerows(results)
file.close()

#print(results)

## IDEA
# Given a song title
# Get recommendations
# Choose the most similar form the data frame
# add to list
# do recs from that track and repeat until limit


#print(sp.audio_analysis(track_ids[0])['track']['codestring'])


# for track in tracks[:10]:
#     title = get_track_title(str(track).strip())
#     print(title)
#     results = sp.search(q=title, type='track')
#     track_id = results['tracks']['items'][0]['id']
#     features = get_track_features(track_id)
#     all_tracks.append(title)
#     all_features.extend(features)

# print(all_features)