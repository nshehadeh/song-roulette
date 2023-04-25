import asyncio
import websockets
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import config
import datetime

"""
Client file contributions
- Matthew
- Nishan

ChatGPT
"""

def setup_spotify():
    """This function sets up the Spotify API client and retrieves the user's recently played songs."""
    global sp
    print("Setting up spotify")
    top_track_ids = []
    limit = 50
    
    # Calculate the timestamp for one week ago
    one_week_ago = int((datetime.datetime.now() - datetime.timedelta(weeks=1)).timestamp()) * 1000

    # Get recently played tracks
    recently_played_tracks = []
    limit = 50
    offset = 0
    
    results = sp.current_user_recently_played(after=one_week_ago)

    # Print the top 5 recent track names
    # Iterate through the recently played tracks and populate the songs list with dictionaries
    songs = []
    for item in results['items']:
        track = item['track']
        songs.append({
            'title': track['name'],
            'artist': track['artists'][0]['name']
        })
    return songs


async def join_game():
    """This function manages the connection with the game server and handles the user's input and interactions during the game."""
    global sp
    uri = "wss://songroulette.herokuapp.com"
    async with websockets.connect(uri) as websocket:
        name = input("Enter your name: ")
        await websocket.send(name)

        welcome_message = await websocket.recv()
        print(welcome_message)
        while True:
            ready = input()
            await websocket.send(ready)
            if ready == "ready":
                break

        # Prepare your list of songs
        your_songs = setup_spotify()

        # Send your songs to the server
        songs_data = json.dumps(your_songs)
        await websocket.send(songs_data)

        # Main game loop
        while True:
            message = await websocket.recv()

            if "Song:" in message:
                print(message)
                vote = input("Who do you think listened to this song? ")
                # Parse the song title and artist from the string
                """
		song_str = message
                song_parts = song_str.split(":")[1].strip().split("by")
                song_title = song_parts[0].strip()
                song_artist = song_parts[1].strip()

                # Search for the song on Spotify
                results = sp.search(q=song_title + " " + song_artist, type='track', limit=1)

                # Check if any results were found
                if len(results['tracks']['items']) == 0:
                    print("Sorry, no results found for that song.")
                else:
                    # Get the Spotify ID of the first result
                    track_id = results['tracks']['items'][0]['id']

                    # Play the song on the user's Spotify app or device
                    sp.start_playback(uris=['spotify:track:' + track_id])
                    print(f"Now playing: {song_title} by {song_artist}")
		"""
                await websocket.send(vote)
            elif "Scoreboard:" in message:
                print(message)
            elif "Game Over!" in message:
                print(message)
                break

async def main():
    """This function serves as the entry point for the program, which initiates the game by calling join_game()."""
    await join_game()

scope = "user-library-read user-top-read user-read-recently-played"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=config.CLIENT_ID, 
                                                   client_secret=config.CLIENT_SECRET, 
                                                   redirect_uri="http://localhost:8888/callback"))   
asyncio.run(main())


