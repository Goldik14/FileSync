#server/api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from server.db.database import get_session
from server.db.models import User
from server.auth.security import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth")

@router.post("/register")
async def register(username: str, password: str, session=Depends(get_session)):
    result = await session.execute(select(User).where(User.username == username))
    if result.scalar():
        raise HTTPException(400, "User already exists")

    user = User(
        username=username,
        password_hash=hash_password(password)
    )
    session.add(user)
    await session.commit()

    return {"status": "ok"}

@router.post("/login")
async def login(username: str, password: str, session=Depends(get_session)):
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(user.id)
    return {"access_token": token, "username": user.username}
