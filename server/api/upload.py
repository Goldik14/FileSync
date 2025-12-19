#server/api/upload.py
import hashlib
import aiofiles
from fastapi import APIRouter, UploadFile, Depends, Header
from server.config import STORAGE_PATH
from server.db.database import get_session
from server.db.crud import add_file
from server.auth.deps import get_current_user
from server.config import user_storage
from server.api.websocket import active_connections
from server.auth.deps import get_current_user
from server.config import user_storage
import json

router = APIRouter(prefix="/upload")

@router.post("/")
async def upload_file(
    file: UploadFile,
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    user_dir = user_storage(user.id)
    path = user_dir / file.filename
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
    for ws in active_connections.get(user.id, []):
        await ws.send_text(json.dumps({
            "action": "add",
            "filename": file.filename
        }))
    return {"status": "ok"}