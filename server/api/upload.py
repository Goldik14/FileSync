#server/api/upload.py
import hashlib
import aiofiles
from fastapi import APIRouter, UploadFile, Depends
from pathlib import Path

from server.config import STORAGE_PATH
from server.db.database import get_session
from server.db.crud import add_file

router = APIRouter(prefix="/upload")

@router.post("/")
async def upload_file(
    file: UploadFile,
    session=Depends(get_session)
    ):
    path = STORAGE_PATH / file.filename
    hasher = hashlib.sha256()

    async with aiofiles.open(path, "wb") as f:
        while chunk := await file.read(8192):
            hasher.update(chunk)
            f.write(chunk)

    await add_file(session, filename=file.filename, file_hash=hasher.hexdigest(), size=path.stat().st_size)

    return {"status": "ok", "filename": file.filename}