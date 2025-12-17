# server/api/devices.py
from fastapi import APIRouter, Depends, Header
from server.db.database import get_session
from server.db.crud import get_or_create_user, register_device

router = APIRouter(prefix="/devices")

@router.post("/register")
async def register(
    device_name: str,
    username: str = Header(...),
    session=Depends(get_session)
):
    user = await get_or_create_user(session, username)
    device = await register_device(session, user.id, device_name)
    return {"device_id": device.id}