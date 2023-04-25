import asyncio
import websockets
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import config
import datetime


scope = "user-library-read user-top-read user-read-recently-played app-remote-control user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=config.CLIENT_ID, 
                                                   client_secret=config.CLIENT_SECRET, 
                                                   redirect_uri="http://localhost:8888/callback"))   
print("Setting up spotify")
top_track_ids = []
limit = 50
# top tracks?
# Calculate the timestamp for one week ago

# Get recently played tracks
recently_played_tracks = []
limit = 50
offset = 0

results = sp.current_user_recently_played()

songs = []
for item in results['items']:
    track = item['track']
    songs.append({
        'title': track['name'],
        'artist': track['artists'][0]['name']
    })
print(songs)

message = "Song: Runaway (U & I) - Ansolo Remix by Galantis"

if "Song:" in message:
    print(message)
    # Parse the song title and artist from the string
    song_str = message
    song_parts = song_str.split(":")[1].strip().split("by")
    song_title = song_parts[0].strip()
    song_artist = song_parts[1].strip()

    # Search for the song on Spotify
    print("title: ", song_title)
    print("artist: ", song_artist)
    q = "track:{song_title} artist:{song_artist}"
    query = f"track:{song_title.replace(' ', '%')}%artist:{song_artist.replace(' ', '%')}"
    query = f"remaster%20track:Doxy%20artist:Miles%20Davis"
    print(query)
    results= sp.search("track:Runaway%(U%&%I)", type='track')
    print("Result", results)
    # Check if any results were found
    if len(results['tracks']['items']) == 0:
        print("Sorry, no results found for that song.")
    else:
        # Get the Spotify ID of the first result
        track_id = results['tracks']['items'][0]['id']

        # Play the song on the user's Spotify app or device
        sp.start_playback(uris=['spotify:track:' + track_id])
        print(f"Now playing: {song_title} by {song_artist}")
