#server/api/sync.py
from fastapi import APIRouter, Depends, Header
from server.db.database import get_session
from server.db.crud import get_user_files, get_or_create_user

router = APIRouter(prefix="/sync")

@router.post("/")
async def sync(
    client_files: list[str],
    username: str = Header(...),
    session=Depends(get_session)
):
    user = await get_or_create_user(session, username)
    server_files = await get_user_files(session, user.id)

    missing = [
        f.filename for f in server_files
        if f.filename not in client_files
    ]
    return {"missing": missing}
