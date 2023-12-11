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


# Dictionary mapping phone numbers to Contact Names
name_dict = {
    '+1234567891' : 'Name',
}

# Replace the below path with the full path of your chat.db file
conn = sqlite3.connect('/full/path/to/your/chat.db')

# Execute the SQL query that grabs all messages from a certain group / person
# Replace the chat ID with the ID of your conversation
cursor = conn.cursor()
main_df = pd.read_sql_query("SELECT * FROM message LEFT JOIN handle ON message.handle_id = handle.ROWID WHERE cache_roomnames like '%chatxxxxxxxxxxxxxxxxxxxx%'", conn)

# Initializations of blocklist for reactions and storage arrays
reacts = ["Loved", "Emphasized", "Laughed at", "Liked"]
messages=[]
names = {}
id_messages = {}

# This method returns True if the string provided is a Spotify link to a song, not an album or playlist
def isLink(message):
    if "http://" in message or "https://" in message:
        if "open.spotify" in message and "album" not in message and "playlist" not in message:
            return True


# Iterate over the rows returned from the SQL query
for i, row in main_df.iterrows():

    # Transpose the row to index the columns
    rpd = pd.DataFrame(row)
    rpdt = rpd.T

    # If the entry in the dataframe is a Spotify link and NOT a reaction to a message
    if not any([x in str(rpdt.loc[i]['text']) for x in reacts]) and isLink(str(rpdt.loc[i]['text'])):
    
        print("-----------------------------------")

        print(str(rpdt.loc[i]['id']))
        print(str(rpdt.loc[i]['text']))
        print(name_dict.get(str(rpdt.loc[i]['id'])))

        # Display the information (ID, link, Sender name) and add to dictionary

        id_messages[str(rpdt.loc[i]['text'])] = name_dict.get(str(rpdt.loc[i]['id']))

        print("-----------------------------------")

# Replace with your own credentials for the Spotify API
client_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
client_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# This method gets track features from Spotify API given a track ID
def get_track_features(track_id):
    track_features = sp.audio_features(track_id)
    return track_features

# Initialize an empty list to store the track features and names
all_features = []
all_tracks = []
all_names = []


# This method extracts the track title from a Spotify URL
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

# Iterate over the entries in the dictionary with names
for song in id_messages:
    title = get_track_title(str(song).strip())
    print(title)
    if title:
        # Use the track title to get the features of the track from Spotify API
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

# Perform simple 2 component PCA on the standardized features
pca = PCA(n_components=2)
principal_components = pca.fit_transform(features)
principal_df = pd.DataFrame(data=principal_components, columns=["PC1", "PC2"])

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