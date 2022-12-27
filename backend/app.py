import logging
import json
import uvicorn
import randomname

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)

# Map of connections, where the key is the player ID and the value is the WebSocket connection
connections = {}

# Map of games, where the key is the game ID and the value is a tuple ({player1id: move}, {player2id:move})
games = {}

logging.basicConfig(level=logging.INFO)
app = FastAPI()
app.mount("/static", StaticFiles(directory="../web"), name="static")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  player_id = randomname.generate('a/', 'a/', 'n/')
  while (player_id in games.keys()):
    player_id = randomname.generate('a/', 'a/', 'n/')

  game_id = player_id
  logging.info(f"New player connected {player_id}")
  connections[player_id] = websocket
  games[player_id] = ({"id": player_id, "move": None}, None)
  await websocket.send_json({"action": "waiting", "game": player_id})
  try:
    while True:
      data = await websocket.receive_json()
      print(data)
      ###########################
      # Game join               #
      ###########################
      if data["action"] == "join_game":
        # Join an existing game
        game_id = data["gameId"]
        if game_id == player_id:
          # Player trying to join own game
          await websocket.send_json({
              "action": "error",
              "message": "you can't join your own game"
          })
        elif game_id in games:
          player1, player2 = games[game_id]
          if player2 is None:
            logging.info(f"Player 2 joined for game {game_id}")
            del games[player_id]
            games[game_id] = (player1, {"id": player_id, "move": None})
            await connections[player1["id"]].send_json({"action": "start_game"})
            await websocket.send_json({"action": "start_game"})
          else:
            logging.info(f"Room is full for game {game_id}")
            await websocket.send_json({
                "action": "error",
                "message": "Game full. Maybe you're already part of the game?"
            })
      ###########################
      # Player move             #
      ###########################
      if data["action"] == "make_move":
        # Make a move in an existing game
        print(data)
        move = data["move"]
        logging.info(f"Game {game_id} - {move}")
        if game_id in games.keys():
          player1, player2 = games[game_id]
          if player_id == player1["id"]:
            games[game_id] = ({"id": player1["id"], "move": move}, player2)
          elif player_id == player2["id"]:
            games[game_id] = (player1, {"id": player2["id"], "move": move})
          else:
            await websocket.send("error:invalid_player")
          await check_games(game_id)
        else:
          await websocket.send("error:invalid_game")
  except WebSocketDisconnect:
    logging.info(f"Client disconnected: {player_id}")
  except json.decoder.JSONDecodeError:
    await websocket.send_json({
        "action": "error",
        "message": "Badly formatted message. Disconnecting."
    })


async def check_games(game_id):
  (player1, player2) = games[game_id]
  if isinstance(player1["move"], str) and isinstance(player2["move"], str):
    # Determine the winner of the game
    if player1["move"] == player2["move"]:
      result = -1
    elif (player1["move"] == "rock" and player2["move"] == "scissors") or (
        player1["move"] == "scissors" and
        player2["move"] == "paper") or (player1["move"] == "paper" and
                                        player2["move"] == "rock"):
      result = 0
    else:
      result = 1
    # Send the result to both players
    await connections[games[game_id][0]["id"]].send_json({
        "action": "result",
        "result": "draw" if result == -1 else "win" if result == 0 else "lose"
    })
    await connections[games[game_id][1]["id"]].send_json({
        "action": "result",
        "result": "draw" if result == -1 else "win" if result == 1 else "lose"
    })
    # Remove the moves from the game
    games[game_id] = ({
        "id": games[game_id][0]["id"],
        "move": None
    }, {
        "id": games[game_id][1]["id"],
        "move": None
    })


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
