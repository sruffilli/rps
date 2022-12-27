import logging
import json
import uvicorn
import randomname
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)

# Map of connections, where the key is the player ID and the value is the WebSocket connection
connections = {}

# Map of games, where the key is the game ID and the value is a tuple ({player1id: move}, {player2id:move})
games = {}

logging.basicConfig(level=logging.INFO)
app = FastAPI()
app.mount(
    "/web",
    StaticFiles(
        directory=f"{os.path.dirname(os.path.abspath(__file__))}/../web"),
    name="web")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  player_id = randomname.generate('a/', 'a/', 'n/')
  while (player_id in games.keys()):
    player_id = randomname.generate('a/', 'a/', 'n/')

  game_id = player_id
  logging.info(f"New player connected {player_id}")
  connections[player_id] = websocket
  games[player_id] = ({1: {"id": player_id, "move": None}, 2: None})
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
          p1 = games[game_id][1]
          p2 = games[game_id][2]
          if p2 is None:
            logging.info(f"Player 2 joined for game {game_id}")
            del games[player_id]
            games[game_id][2] = {"id": player_id, "move": None}
            await connections[p1["id"]].send_json({"action": "start_game"})
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
        game_player = [
            x for x in games[game_id] if games[game_id][x]["id"] == player_id
        ][0]
        games[game_id][game_player]["move"] = move
        await check_games(game_id)

  except WebSocketDisconnect:
    ###########################
    # Player disconnects      #
    ###########################
    logging.info(f"Client disconnected: {player_id}, {game_id}")
    del connections[player_id]
    left_player_id = [
        games[game_id][x]["id"]
        for x in games[game_id]
        if games[game_id][x]["id"] != player_id
    ][0]
    if left_player_id in connections:
      await connections[left_player_id].send_json(
          {"action": "player_disconnected"})
  except json.decoder.JSONDecodeError:
    await websocket.send_json({
        "action": "error",
        "message": "Badly formatted message. Disconnecting."
    })


async def check_games(game_id):
  p1 = games[game_id][1]
  p2 = games[game_id][2]
  if isinstance(p1["move"], str) and isinstance(p2["move"], str):
    # Determine the winner of the game
    if p1["move"] == p2["move"]:
      result = -1
    elif (p1["move"] == "rock" and p2["move"] == "scissors") or (
        p1["move"] == "scissors" and
        p2["move"] == "paper") or (p1["move"] == "paper" and
                                   p2["move"] == "rock"):
      result = 0
    else:
      result = 1
    # Send the result to both players
    await connections[games[game_id][1]["id"]].send_json({
        "action": "result",
        "result": "draw" if result == -1 else "win" if result == 0 else "lose"
    })
    await connections[games[game_id][2]["id"]].send_json({
        "action": "result",
        "result": "draw" if result == -1 else "win" if result == 1 else "lose"
    })
    # Remove the moves from the game
    games[game_id] = {
        1: {
            "id": games[game_id][1]["id"],
            "move": None
        },
        2: {
            "id": games[game_id][2]["id"],
            "move": None
        }
    }


if __name__ == "__main__":
  uvicorn.run(
      "app:app", reload=True, host="0.0.0.0", port=8080, log_level="info")
