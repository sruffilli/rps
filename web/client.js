const serverUrl = `ws://${window.location.host}/ws`;

let websocket;
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

function clickMove(move) {
  resetUI();
  document.getElementById(move).classList.add("clicked")
}

function preventJoin() {
  document.getElementById("game-id").setAttribute("disabled", "disabled");
  document.getElementById("join-game").setAttribute("disabled", "disabled");
}

function enableJoin() {
  document.getElementById("game-id").removeAttribute("disabled");
  document.getElementById("join-game").removeAttribute("disabled");
}

function activateMoves() {
  document.getElementById("rock").classList.add("breathing");
  document.getElementById("paper").classList.add("breathing");
  document.getElementById("scissors").classList.add("breathing");
}

function startGame() {
  resetUI();
  preventJoin();
  activateMoves();
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

function updateScoreBoard() {
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
    const message = JSON.parse(event.data);
    const action = message.action;
    switch (action) {
      case "waiting":
        const urlParams = new URLSearchParams(window.location.search);
        const joinGameFromUrl = urlParams.get('join')
        if (joinGameFromUrl) {
          joinGame(joinGameFromUrl);
          document.getElementById("game-id").value = joinGameFromUrl;
        } else {
          // Display a message indicating that the player is waiting for an opponent
          document.getElementById("game-id").value = message.game;
          console.log("Waiting for an opponent");
        }
        break;
      case "start_game":
        // Store the game ID and start the game
        startGame();
        console.log("Game started");
        break;
      case "error":
        // Display a message indicating that the player is waiting for an opponent
        displayMessage(message.message);
        break;
      case "result":
        // Display the result of the game
        let resultMessage;
        switch (message.result) {
          case "draw":
            resultMessage = "☮️ Draw game ☮️"
            break;
          case "win":
            resultMessage = "🥳 You WON! 🥳"
            score.self += 1;
            break;
          case "lose":
            resultMessage = "😒 You LOST! 😒"
            score.opponent += 1;
            break;
          default:
            break;
        }
        updateScoreBoard();
        displayMessage(resultMessage);
        break;
      default:
        // Default case
        console.log("Invalid action");
    }
  };
  return websocket;
}

function initGame() {
  // Send a message to the server to init a new game
  websocket.send("init_game");
}

function joinGame() {
  console.log(`Joining game specified in game bar`)
  joinGame(document.getElementById("game-id").value);
}

function joinGame(game) {
  console.log(`Joining game ${game}`)
  // Send a message to the server to join an existing game
  res = {
    "action": "join_game",
    "gameId": game
  }
  console.log(res)
  websocket.send(JSON.stringify(res));
}

function makeMove(move) {
  // Send a message to the server to make a move
  clickMove(move);
  res = {
    "action": "make_move",
    "move": move
  }
  console.log(res)
  websocket.send(JSON.stringify(res));
}

connect();
