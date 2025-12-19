# server/api/devices.py
from fastapi import APIRouter, Depends, Header
from server.db.database import get_session
from server.db.crud import get_or_create_user, register_device
from server.auth.deps import get_current_user

router = APIRouter(prefix="/devices")

@router.post("/register")
async def register(
    device_name: str,
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    device = await register_device(session, user.id, device_name)
    return {"device_id": device.id}