import asyncio
import logging
import uuid

import websockets

# Set up logging
logging.basicConfig(level=logging.INFO)

# Map of connections, where the key is the player ID and the value is the WebSocket connection
connections = {}

# Map of games, where the key is the game ID and the value is a tuple ({player1id: move}, {player2id:move})
games = {}


async def handle_connection(websocket, path):
  # Assign a unique player ID to the connection
  player_id = str(uuid.uuid4())
  connections[player_id] = websocket
  client_ip = websocket.remote_address[0]
  await websocket.send(f'player_id:{player_id}')
  logging.info(f'New connection from {client_ip}')
  try:
    async for message in websocket:
      # Parse the message
      message = message.split(':')
      action = message[0]
      match action:
        case 'init_game':
          # Start a new game
          game_id = str(uuid.uuid4())
          games[game_id] = ({"id": player_id, "move": None}, None)
          logging.info(f'Init game {game_id}')
          await websocket.send(f'waiting:{game_id}')
        case 'join_game':
          # Join an existing game
          game_id = message[1]
          if game_id in games:
            player1, player2 = games[game_id]
            if player2 is None:
              logging.info(f'Player 2 joined for game {game_id}')
              games[game_id] = (player1, {"id": player_id, "move": None})
              await connections[player1["id"]].send(f'start_game:{game_id}:player1')
              await websocket.send(f'start_game:{game_id}:player2')
            else:
              logging.info(f'Room is full for game {game_id}')
              await websocket.send('error:game_full')
        case 'make_move':
          # Make a move in an existing game
          print(message)
          game_id = message[1]
          move = message[2]
          logging.info(f'Game {game_id} - {move}')
          if game_id in games.keys():
            player1, player2 = games[game_id]
            if player_id == player1["id"]:
              games[game_id] = ({"id": player1["id"], "move": move}, player2)
            elif player_id == player2["id"]:
              games[game_id] = (player1, {"id": player2["id"], "move": move})
            else:
              await websocket.send('error:invalid_player')
          else:
            await websocket.send('error:invalid_game')
        case 'get_game_state':
          # Get the current state of a game
          game_id = message[1]
          logging.info(f'Gamestate for {game_id}')
          if game_id in games:
            player1, player2 = games[game_id]
            if player1 and player2:
              await websocket.send(f'game_state:{player1}:{player2}')
            else:
              await websocket.send('game_state:waiting')
          else:
            await websocket.send('error:invalid_game')
  finally:
    # Remove the connection from the list of connections
    del connections[player_id]


async def check_games():
  while True:
    for game_id, (player1, player2) in list(games.items()):
      if isinstance(player1["move"], str) and isinstance(player2["move"], str):
        # Determine the winner of the game
        if player1["move"] == player2["move"]:
          result = 'draw'
        elif (player1["move"] == 'rock' and player2["move"] == 'scissors') or (
            player1["move"] == 'scissors' and
            player2["move"] == 'paper') or (player1["move"] == 'paper' and
                                            player2["move"] == 'rock'):
          result = 'player1'
        else:
          result = 'player2'
        # Send the result to both players
        await connections[games[game_id][0]["id"]].send(f'result:{result}')
        await connections[games[game_id][1]["id"]].send(f'result:{result}')
        # Remove the game from the list of games
        games[game_id] = (
          {"id": games[game_id][0]["id"], "move": None},
          {"id": games[game_id][1]["id"], "move": None}
        )
    # Pause for a short period of time before checking again
    await asyncio.sleep(0.1)


async def main():
  server = await websockets.serve(handle_connection, 'localhost', 8080)
  asyncio.create_task(check_games())
  await server.wait_closed()


asyncio.run(main())