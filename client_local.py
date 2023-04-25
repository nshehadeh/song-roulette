import asyncio
import websockets
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import config
import datetime

def setup_spotify():
    print("Setting up spotify")
    scope = "user-library-read user-top-read user-read-recently-played"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=config.CLIENT_ID, 
                                                   client_secret=config.CLIENT_SECRET, 
                                                   redirect_uri="http://localhost:8888/callback"))
    top_track_ids = []
    limit = 50
    # top tracks?
    """
    for i in range(20):  # Retrieve 20 pages of top tracks (20 * 50 = 1000 tracks)
        top_tracks_results = sp.current_user_top_tracks(limit=limit, offset=i * limit, time_range='short_term')
        top_track_ids.extend([track['id'] for track in top_tracks_results['items']])
    """
    # Calculate the timestamp for one week ago
    one_week_ago = int((datetime.datetime.now() - datetime.timedelta(weeks=1)).timestamp()) * 1000

    # Get recently played tracks
    recently_played_tracks = []
    limit = 50
    offset = 0
    
    results = sp.current_user_recently_played(after=one_week_ago)
    #recent_track_ids = [track['track']['id'] for track in recently_played_tracks]

    # Find the intersection of top tracks and recently played tracks
    #top_recent_track_ids = list(set(top_track_ids).intersection(recent_track_ids))[:50]

    # Print the top 5 recent track names
    songs = []
    for track_id in recently_played_tracks[:5]:
        track = sp.track(track_id)
        songs.append(track['name'])
    return recently_played_tracks, songs


async def join_game():
    uri = "ws://localhost:8765"
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
        your_songs = [
            {"title": "Song 1", "artist": "Artist 1"},
            {"title": "Song 2", "artist": "Artist 2"},
            {"title": "Song 3", "artist": "Artist 3"},
        ]

        # Send your songs to the server
        songs_data = json.dumps(your_songs)
        await websocket.send(songs_data)

        # Main game loop
        while True:
            message = await websocket.recv()

            if "Song:" in message:
                print(message)
                vote = input("Who do you think listened to this song? ")
                await websocket.send(vote)
            elif "Scoreboard:" in message:
                print(message)
            elif "Game Over!" in message:
                print(message)
                break

async def main():
    await join_game()

asyncio.run(main())


