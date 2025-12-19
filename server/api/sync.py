#server/api/sync.py
from fastapi import APIRouter, Depends, Header
from server.db.database import get_session
<<<<<<< HEAD
from server.db.crud import get_user_files, get_or_create_user
=======
from server.db.crud import get_user_files
>>>>>>> rework-auth
from server.auth.deps import get_current_user

router = APIRouter(prefix="/sync")

@router.post("/")
async def sync(
    client_files: list[str],
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    server_files = await get_user_files(session, user.id)
    missing = [
        f.filename for f in server_files
        if f.filename not in client_files
    ]
    return {"missing": missing}
