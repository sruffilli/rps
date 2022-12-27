import pytest


@pytest.mark.asyncio
async def test_websocket_endpoint(app, client):
  # Connect to the WebSocket endpoint
  ws = await client.websocket("/ws")

  # Send a message over the WebSocket connection
  await ws.send_text("hello")

  # Receive the response from the WebSocket endpoint
  response = await ws.receive_text()

  # Verify that the response is the same as the message that was sent
  assert response == "hello"


@pytest.fixture
def app():
  from app import app
  return app


@pytest.fixture
def client(app):
  return TestClient(app)