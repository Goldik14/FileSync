#server/api/websocket.py
from fastapi import APIRouter, WebSocket
from server.api.upload import active_connections

router = APIRouter(prefix="/ws")

@router.websocket("/")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_connections.append(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        pass
    finally:
        active_connections.remove(ws)