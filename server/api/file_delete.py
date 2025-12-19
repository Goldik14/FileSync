# server/api/file_delete.py
from fastapi import APIRouter, Depends, HTTPException
from server.db.database import get_session
from server.db.crud import get_file_by_name
from server.api.websocket import active_connections
from server.auth.deps import get_current_user
from server.config import user_storage
import json
import os

router = APIRouter(prefix="/file")

@router.post("/delete")
async def delete_file(
    filename: str,
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    file = await get_file_by_name(session, filename)
    if not file or file.user_id != user.id:
        raise HTTPException(status_code=404, detail="Файл не найден")
    path = user_storage(user.id) / filename

    if path.exists():
        os.remove(path)
    await session.delete(file)
    await session.commit()
    for ws in active_connections.get(user.id, []):
        await ws.send_text(json.dumps({
            "action": "delete",
            "filename": filename
        }))
    return {"status": "ok"}