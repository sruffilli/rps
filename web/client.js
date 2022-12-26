const serverUrl = "ws://localhost:8000/ws";

let websocket;
let gameId;
let playerId;
let player;
let interval;
let score = {
  "self": 0,
  "opponent": 0
}

function resetUI() {
  document.getElementById("moves").classList.remove("blurred");
  document.getElementById("overlay").style.setProperty("display", "none", "important");
  document.getElementById("overlay").innerText = "";
  document.getElementById("rock").classList.remove("clicked");
  document.getElementById("paper").classList.remove("clicked");
  document.getElementById("scissors").classList.remove("clicked");
}

function displayMessage(message) {
  document.getElementById("moves").classList.add("blurred");
  document.getElementById("overlay").style.setProperty("display", "flex");
  document.getElementById("overlay").innerText = message;
  interval = setInterval(function () {
    resetUI();
    clearInterval(interval);
  }, 2000)
}

function updateScore() {
  document.getElementById("self-score").innerText = score.self;
  document.getElementById("opponent-score").innerText = score.opponent;
}

function connect() {
  // Connect to the WebSocket server
  websocket = new WebSocket(serverUrl);

  // Set up event listeners for the WebSocket events
  websocket.onopen = function (event) {
    console.log("Connected to server");
  };

  websocket.onclose = function (event) {
    console.log("Disconnected from server");
  };

  websocket.onmessage = function (event) {
    // Parse the message from the server
    console.log(event)
    const message = event.data.split(":");
    const action = message[0];
    switch (action) {
      case "player_id":
        playerId = message[1]
        console.log("PlayerID:" + playerId);
        initGame();
        break;
      case "waiting":
        // Display a message indicating that the player is waiting for an opponent
        gameId = message[1];
        document.getElementById("game-id").value = gameId;
        console.log("Waiting for an opponent");
        break;
      case "start_game":
        // Store the game ID and start the game
        gameId = message[1];
        player = message[2];
        resetUI();
        console.log("Game started");
        break;
      case "game_state":
        // Update the game state
        const player1 = message[1];
        const player2 = message[2];
        console.log(`Game state: ${player1} vs ${player2}`);
        break;
      case "result":
        // Display the result of the game
        const winningplayer = message[1];
        const didIWin = winningplayer == player;
        const draw = winningplayer == "draw"

        if (draw) {
          displayMessage("Draw game!")
        } else {
          score.self += didIWin ? 1 : 0;
          score.opponent += didIWin ? 0 : 1;
          displayMessage(`YOU ${didIWin ? "WON" : "LOST"}`);
          updateScore();
        }

        console.log(`Result: ${winningplayer}`);
        break;
      case "error":
        // Display an error message
        const error = message[1];
        console.log(`Error: ${error}`);
        break;
      default:
        // Default case
        console.log("Invalid action");
    }

  };
}

function initGame() {
  // Send a message to the server to init a new game
  self.send_message("init_game");
}

function joinGame() {
  // Send a message to the server to join an existing game
  self.send_message(`join_game:${document.getElementById("game-id").value}`);
}

function makeMove(move) {
  // Send a message to the server to make a move
  document.getElementById(move).classList.add("clicked")
  self.send_message(`make_move:${gameId}:${move}`);
}

function getGameState() {
  // Send a message to the server to get the current state of the game
  self.send_message(`get_game_state:${gameId}`);
}

connect();