#server/api/upload.py
import hashlib
import aiofiles
from fastapi import APIRouter, UploadFile, Depends
from server.config import STORAGE_PATH
from server.db.database import get_session
from server.db.crud import add_file
from typing import List
from fastapi import WebSocket

router = APIRouter(prefix="/upload")
active_connections: List[WebSocket] = []

@router.post("/")
async def upload_file(file: UploadFile, session=Depends(get_session)):
    path = STORAGE_PATH / file.filename
    hasher = hashlib.sha256()

    async with aiofiles.open(path, "wb") as f:
        while chunk := await file.read(8192):
            hasher.update(chunk)
            await f.write(chunk)

    await add_file(session, file.filename, hasher.hexdigest(), path.stat().st_size)

    # Уведомляем всех подключенных WebSocket клиентов
    for ws in active_connections:
        try:
            await ws.send_json({"filename": file.filename})
        except:
            pass

    return {"status": "ok", "filename": file.filename}