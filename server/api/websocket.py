#server/api/websocket.py
from fastapi import APIRouter, WebSocket
from server.auth.security import decode_token

router = APIRouter(prefix="/ws")

active_connections: dict[int, list[WebSocket]] = {}

@router.websocket("/")
async def websocket_endpoint(ws: WebSocket, token: str):
    user_id = decode_token(token)
    await ws.accept()
<<<<<<< HEAD
    active_connections.setdefault(user_id, []).append(ws)
=======

    active_connections.setdefault(user_id, []).append(ws)

>>>>>>> rework-auth
    try:
        while True:
            await ws.receive_text()
    finally:
<<<<<<< HEAD
        active_connections[user_id].remove(ws)
=======
        active_connections[user_id].remove(ws)
>>>>>>> rework-auth
