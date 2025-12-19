#server/api/download.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from server.auth.deps import get_current_user
from server.config import user_storage

router = APIRouter(prefix="/download")

@router.get("/{filename}")
async def download_file(
    filename: str,
    user=Depends(get_current_user)
):
    path = user_storage(user.id) / filename
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path)
