const serverUrl = `ws://${window.location.host}/ws`;

let websocket;
let interval;
let messageOutInterval;
let vibrateInterval;
let ephemeralMessageInterval;
let score = {
  "self": 0,
  "opponent": 0
}

/*
 * Websocket connection and message handling
 */

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
          document.getElementById("game-id").value = message.game;
          console.log("Waiting for an opponent");
        }
        break;
      case "start_game":
        // Store the game ID and start the game
        startGame();
        console.log("Game started");
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
        showEphemeralMessage(resultMessage);
        resetUI();
        break;
      case "player_disconnected":
        showMessage("Player Disconnected. Refresh for a new game.");
        break;
      case "error":
        // Display a message indicating that the player is waiting for an opponent
        showMessage("Something weird happened and I give up. Refresh for a new game!");
        break;
      default:
        // Default case
        console.log("Invalid action");
    }
  };
  return websocket;
}

/*
 * In-game actions
 */

function startGame() {
  preventJoin();
  resetUI();
  unblockUI();
  showEphemeralMessage("FIGHT!")
}

function updateScoreBoard() {
  document.getElementById("self-score").innerText = score.self;
  document.getElementById("opponent-score").innerText = score.opponent;
}

function initGame() {
  // Send a message to the server to init a new game
  websocket.send("init_game");
}

function joinGameByInput() {
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

/*
 * UI/UX
 */

function resetUI() {
  document.getElementById("rock").classList.remove("clicked");
  document.getElementById("paper").classList.remove("clicked");
  document.getElementById("scissors").classList.remove("clicked");
}

function blockUI() {
  document.getElementById("rock").setAttribute("disabled", "disabled");
  document.getElementById("paper").setAttribute("disabled", "disabled");
  document.getElementById("scissors").setAttribute("disabled", "disabled");
  document.getElementById("rock").classList.remove("breathing");
  document.getElementById("paper").classList.remove("breathing");
  document.getElementById("scissors").classList.remove("breathing");
}

function unblockUI() {
  document.getElementById("rock").removeAttribute("disabled");
  document.getElementById("paper").removeAttribute("disabled");
  document.getElementById("scissors").removeAttribute("disabled");
  document.getElementById("rock").classList.add("breathing");
  document.getElementById("paper").classList.add("breathing");
  document.getElementById("scissors").classList.add("breathing");
}

function messageIn() {
  blockUI();
  document.getElementById("board").classList.add("blurred");
  document.getElementById("message-box-overlay").style.display = "table";
  document.getElementById("message-box").classList.remove("slide-out-blurred-right");
  document.getElementById("message-box").classList.add("slide-in-blurred-left");
}

function messageOut() {
  document.getElementById("message-box").classList.remove("vibrate");
  document.getElementById("message-box").classList.remove("slide-in-blurred-left");
  document.getElementById("message-box").classList.add("slide-out-blurred-right");
  messageOutInterval = setInterval(function () {
    document.getElementById("message-box-overlay").style.display = "none";
    unblockUI();
    document.getElementById("board").classList.remove("blurred");
    clearInterval(messageOutInterval);
  }, 500)
}

function showMessage(message, options) {
  options ??= {};
  document.getElementById("message").innerText = message;
  if (document.getElementById("message-box-overlay").style.display == "table") {
    document.getElementById("message-box").classList.remove("slide-in-blurred-left");
    document.getElementById("message-box").classList.add("vibrate");
  } else {
    messageIn();
  }
}

function showEphemeralMessage(message, timer) {
  timer ??= 1500;
  showMessage(message);
  ephemeralMessageInterval = setInterval(function () {
    messageOut();
    clearInterval(ephemeralMessageInterval);
  }, timer)
}

function clickMove(move) {
  resetUI();
  document.getElementById(move).classList.add("clicked")
  blockUI();
}

function preventJoin() {
  document.getElementById("game-id").setAttribute("disabled", "disabled");
  document.getElementById("join-game").setAttribute("disabled", "disabled");
}

function enableJoin() {
  document.getElementById("game-id").removeAttribute("disabled");
  document.getElementById("join-game").removeAttribute("disabled");
}

connect();
showMessage("Waiting for an opponent...")
