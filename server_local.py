import asyncio
import websockets
import json
import random
from asyncio.locks import Lock


async def display_ready_status():
    global players, ready_players
    while True:
        if len(ready_players) != len(players):
            remaining_players = len(players) - len(ready_players)
            print(f"{remaining_players} players need to ready up.")
        await asyncio.sleep(5)


async def wait_for_players(websocket, path):
    global players, ready_players, songs, scores, lock

    # Register player
    player_name = await websocket.recv()

    async with lock:
        players[player_name] = websocket
        print(f"{player_name} joined the game.")

    # Wait for player to be ready
    await websocket.send("Welcome! Type 'ready' to start playing.")
    while True:
        message = await websocket.recv()
        if message == "ready":
            async with lock:
                ready_players.add(player_name)
                scores[player_name] = 0
                print(f"{player_name} is ready.")
                if len(ready_players) >= 3 and not game_in_progress:
                    asyncio.create_task(run_game())  # Start the game
            break
        await asyncio.sleep(1)

    # Wait for the game to start
    while not game_in_progress:
        await asyncio.sleep(1)

    # Gather songs from the player
    songs_data = await websocket.recv()

    async with lock:
        songs[player_name] = json.loads(songs_data)
        update_song_pool(player_name)  # Update the song pool with the new player

    # Wait for game updates
    while game_in_progress:
        await asyncio.sleep(1)

async def run_game():
    global game_in_progress, song_pool, players, songs, scores
    game_in_progress = True
    # make sure to get all songs first
    while len(songs) != len(players):
        await asyncio.sleep(1)
    print("Starting Game")
    # While no one has won yet
    while max(scores.values()) < 10:
        # Choose a random song and player
        chosen_player, chosen_song = random.choice([(k, s) for k, v in songs.items() for s in v])

        # Send the song to all players and get their votes
        votes = {}
        print("About to send to: ", players.items())
        for player_name, websocket in dict(players).items():
            try:
                print(f"Sending song to {player_name}")  # Debug print
                await websocket.send(f"Song: {chosen_song['title']} by {chosen_song['artist']}")
                votes[player_name] = await websocket.recv()
            except websockets.exceptions.ConnectionClosedError:
                print(f"{player_name} has been disconnected.")
                async with lock:
                    del players[player_name]

        # Update scores
        for player_name, vote in votes.items():
            if vote == chosen_player:
                scores[player_name] += 1

        # Update scoreboard
        scoreboard = json.dumps(scores)
        for websocket in players.values():
            await websocket.send(f"Scoreboard: {scoreboard}")

    # Announce the winner
    winner = max(scores, key=scores.get)
    for websocket in players.values():
        await websocket.send(f"Game Over! The winner is {winner} with {scores[winner]} points.")

def update_song_pool(player_name):
    global song_pool, songs
    song_pool += [(song, player_name) for song in songs[player_name]]


players = {}
ready_players = set()
songs = {}
scores = {}
game_in_progress = False
song_pool = []
lock = Lock()

start_server = websockets.serve(wait_for_players, "localhost", 8765, ping_timeout=300)
display_status_task = asyncio.ensure_future(display_ready_status())

tasks = asyncio.gather(start_server, display_status_task)
asyncio.get_event_loop().run_until_complete(tasks)
asyncio.get_event_loop().run_forever()
