#server/api/sync.py
from fastapi import APIRouter, Depends
from server.db.database import get_session
from server.db.crud import get_all_files

router = APIRouter(prefix="/sync")

@router.post("/")
async def sync(client_files: list[str], session=Depends(get_session)):
    server_files = await get_all_files(session)
    missing = [f.filename for f in server_files if f.filename not in client_files]
    return {"missing": missing}