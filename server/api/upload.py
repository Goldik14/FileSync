#server/api/upload.py
import hashlib
import aiofiles
from fastapi import APIRouter, UploadFile, Depends, Header
from server.config import STORAGE_PATH
from server.db.database import get_session
from server.db.crud import add_file, get_or_create_user
from server.api.websocket import active_connections
import json

router = APIRouter(prefix="/upload")

@router.post("/")
async def upload_file(
    file: UploadFile,
    session=Depends(get_session),
    username: str = Header(...)
):
    user = await get_or_create_user(session, username)
    path = STORAGE_PATH / file.filename
    hasher = hashlib.sha256()
    async with aiofiles.open(path, "wb") as f:
        while chunk := await file.read(8192):
            hasher.update(chunk)
            await f.write(chunk)
    await add_file(
        session,
        user_id=user.id,
        filename=file.filename,
        file_hash=hasher.hexdigest(),
        size=path.stat().st_size
    )
    for ws in active_connections:
        try:
            await ws.send_text(json.dumps({
                "action": "add",
                "filename": file.filename,
                "user_id": user.id
            }))
        except:
            pass
    return {"status": "ok"}