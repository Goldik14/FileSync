#server/auth/deps.py
from fastapi import Header, HTTPException, Depends
from server.auth.security import decode_token
from server.db.database import get_session
from server.db.models import User
from sqlalchemy import select

async def get_current_user(
    authorization: str = Header(...),
    session=Depends(get_session)
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401)

    token = authorization.split(" ")[1]
    user_id = decode_token(token)

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(401)

    return user
