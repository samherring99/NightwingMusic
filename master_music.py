import sqlite3
import re
import markovify
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt
import io    
import pycurl
from bs4 import BeautifulSoup
from urllib.parse import unquote
import json

name_dict = {
    '+1234567891' : 'Name',
}

conn = sqlite3.connect('/full/path/to/your/chat.db')

cursor = conn.cursor()

main_df = pd.read_sql_query("SELECT * FROM message LEFT JOIN handle ON message.handle_id = handle.ROWID WHERE cache_roomnames like '%chatxxxxxxxxxxxxxxxxxxxx%'", conn)

#num_df = pd.read_sql_query("SELECT handle.id, handle.uncanonicalized_id, count(message.handle_id) as message_count FROM message JOIN handle ON message.handle_id = handle.ROWID WHERE cache_roomnames like '%chat466737536442738%' GROUP BY message.handle_id ORDER BY message_count DESC;", conn)

#num_df.columns = ['number', 'something', 'count']

#num_df = num_df.drop('something', axis=1)

#print(num_df)

#rows = cursor.fetchall()
reacts = ["Loved", "Emphasized", "Laughed at", "Liked"]
messages=[]
names = {}
id_messages = {}

def isLink(message):
    if "http://" in message or "https://" in message:
        if "open.spotify" in message and "album" not in message:
            return True

#print(main_df['id'])

for i, row in main_df.iterrows():

    # Convert row to json object and index into dict that way lol

    #row_obj = json.loads(row)

    #print(row_obj)

    # print(dict(row))
    rpd = pd.DataFrame(row)
    rpdt = rpd.T
    #print(rpdt.loc[i]['text'])
    # print(rpdt['text'])
    if not any([x in str(rpdt.loc[i]['text']) for x in reacts]) and isLink(str(rpdt.loc[i]['text'])):
    #     #print(row[2])
    #     messages.append(str(rpdt['text'])
    
        print("-----------------------------------")

        print(str(rpdt.loc[i]['id']))
        print(str(rpdt.loc[i]['text']))
        print(name_dict.get(str(rpdt.loc[i]['id'])))

        id_messages[str(rpdt.loc[i]['text'])] = name_dict.get(str(rpdt.loc[i]['id']))

        print("-----------------------------------")

    #     if not names[str(rpdt['id'])]:
    #         names[str(rpdt['id'])] = 1
    #     else:
    #         names[str(rpdt['id'])] = int(names[rpdt['id']]) + 1
        
    #     id_messages[rpdt['id']] = str(rpdt['text'])
    
#print(len(messages))

#print(names)

# Replace with your own credentials
client_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
client_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# List of albums to analyze
#tracks = messages

# Define a function to get track features from Spotify API
def get_track_features(track_id):
    track_features = sp.audio_features(track_id)
    return track_features

# Initialize an empty list to store the track features and names
all_features = []
all_tracks = []
all_names = []

def get_track_title(url):
    storage = io.BytesIO()
    c = pycurl.Curl()

    track = unquote(url)
    c.setopt(c.URL, str(track))
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    content = storage.getvalue()

    htmlString = storage.getvalue().decode('UTF-8')

    soup = BeautifulSoup(htmlString, "html.parser")
    val = str(soup.find_all('title')).replace("<title>", "")
    cleaned = val.replace("</title>", "")
    cleaned = cleaned.replace("[", "")
    cleaned = cleaned.replace("]", "")
    cleaned = cleaned.replace("|", "")
    cleaned = cleaned.replace("Spotify", "")

    c.close()

    return cleaned


for song in id_messages:
    title = get_track_title(str(song).strip())
    print(title)
    if title:
        results = sp.search(q=title, type='track')
        track_id = results['tracks']['items'][0]['id']
        features = get_track_features(track_id)
        all_tracks.append(title.split("-")[0])
        all_names.append(id_messages.get(song))
        all_features.extend(features)

# Create a dataframe of the track features
df = pd.DataFrame(all_features)

# Create dataframes for the track names and album names
name_df = pd.DataFrame({"track_name": all_tracks, "sender_name": all_names})

# Merge the track features, names, and album names dataframes
df = pd.concat([df, name_df], axis=1)

# Drop any tracks with missing data
df.dropna(inplace=True)

# Extract the track features columns
features = df.drop(["id", "uri", "analysis_url", "track_href", "type", "duration_ms", "time_signature", "mode", "track_name", "sender_name"], axis=1)

print(features)

# Standardize the features
#scaled_features = (features - np.mean(features)) / np.std(features)

#print(scaled_features)

# Perform PCA on the standardized features
pca = PCA(n_components=2)
principal_components = pca.fit_transform(features)
principal_df = pd.DataFrame(data=principal_components, columns=["PC1", "PC2"])

#print(principal_df)
#print(df)

# Add the album names and track names to the principal components dataframe
principal_df["track_name"] = df["track_name"]
principal_df["sender_name"] = df["sender_name"]

print(principal_df)

# Plot the principal components
sns.scatterplot(x="PC1", y="PC2", hue="sender_name", data=principal_df)

# Loop through each point and add a label
for line in range(0, principal_df.shape[0]):
    plt.text(
        principal_df.PC1[line],
        principal_df.PC2[line],
        principal_df.track_name[line],
        horizontalalignment="left",
        fontsize=6,
        color="black"
    )

plt.show()