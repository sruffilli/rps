import logging

import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket
from starlette.routing import Route

logger = logging.getLogger(__name__)


async def homepage(request):
  logger.info("Received request to homepage")
  return HTMLResponse("Miza")


async def websocket_endpoint(websocket):
  logger.info("Received request to websocket endpoint")
  await websocket.accept()
  # Process incoming messages
  while True:
    mesg = await websocket.receive_text()
    logger.info("Received message from client: %s", mesg)
    await websocket.send_text(mesg.replace("Client", "Server"))
  logger.info("Closing websocket connection")
  await websocket.close()


routes = [
    Route("/miza", endpoint=homepage),
    Route("/ws", endpoint=websocket_endpoint),
]

app = Starlette(routes=routes)

if __name__ == '__main__':
  uvicorn.run("app:app", host='0.0.0.0', port=8000, reload=True)
