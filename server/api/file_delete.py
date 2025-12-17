# server/api/file_delete.py
from fastapi import APIRouter, Header, Depends, HTTPException
from server.db.database import get_session
from server.db.crud import get_or_create_user, get_file_by_name
from server.db.models import File
from server.config import STORAGE_PATH
from server.api.websocket import active_connections
import json
import os

router = APIRouter(prefix="/file")

@router.post("/delete")
async def delete_file(filename: str, username: str = Header(...), session=Depends(get_session)):
    user = await get_or_create_user(session, username)
    file = await get_file_by_name(session, filename)
    if not file or file.user_id != user.id:
        raise HTTPException(status_code=404, detail="Файл не найден")
    path = STORAGE_PATH / filename
    if path.exists():
        os.remove(path)
    await session.delete(file)
    await session.commit()
    for ws in active_connections:
        await ws.send_text(json.dumps({
            "action": "delete",
            "filename": filename
        }))

    return {"status": "ok"}
