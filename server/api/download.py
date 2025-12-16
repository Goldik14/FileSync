#server/api/download.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from server.config import STORAGE_PATH

router = APIRouter(prefix="/download")

@router.get("/{filename}")
async def download_file(filename: str):
    path = STORAGE_PATH / filename
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(path)