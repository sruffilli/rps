from starlette.testclient import TestClient
from starlette.websockets import WebSocket


def client():
  from app import app
  return TestClient(app)


def test_homepage(client):
  response = client.get("/miza")
  assert response.status_code == 200
  assert response.headers["content-type"] == "text/html; charset=utf-8"
  assert response.text == "Miza"


def test_websocket_endpoint(client):
  # Establish websocket connection
  with client.websocket_connect("/ws") as websocket:
    # Send message to server
    websocket.send_text("Client says hello")
    # Receive modified message from server
    response = websocket.receive_text()
    assert response == "Server says hello"


client = client()
test_websocket_endpoint(client)