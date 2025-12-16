#server/db/crud.py
from sqlalchemy import select
from server.db.models import File
from .database import AsyncSessionLocal
from .models import File

async def get_all_files(session):
    result = await session.execute(select(File))
    return result.scalars().all()

async def get_file_by_name(session, filename: str):
    result = await session.execute(
    select(File).where(File.filename == filename)
    )
    return result.scalar_one_or_none()

async def add_file(session, filename, file_hash, size):
    result = await session.execute(select(File).where(File.filename == filename))
    file = result.scalar_one_or_none()
    if file:
        file.hash = file_hash
        file.size = size
    else:
        file = File(filename=filename, hash=file_hash, size=size)
        session.add(file)
    await session.commit()
    return file