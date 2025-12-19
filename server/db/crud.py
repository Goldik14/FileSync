#server/db/crud.py
from sqlalchemy import select
from server.db.models import File, User, Device

async def get_user_files(session, user_id: int):
    result = await session.execute(
        select(File).where(File.user_id == user_id)
    )
    return result.scalars().all()

async def get_file_by_name(session, filename: str):
    result = await session.execute(select(File).where(File.filename == filename))
    return result.scalar_one_or_none()

async def add_file(session, user_id, filename, file_hash, size):
    result = await session.execute(
        select(File).where(
            File.filename == filename,
            File.user_id == user_id
        )
    )
    file = result.scalar_one_or_none()
    if file:
        file.hash = file_hash
        file.size = size
    else:
        file = File(
            filename=filename,
            hash=file_hash,
            size=size,
            user_id=user_id
        )
        session.add(file)
    await session.commit()
    return file

async def register_device(session, user_id: int, device_name: str):
    result = await session.execute(
        select(Device).where(
            Device.user_id == user_id,
            Device.device_name == device_name
        )
    )
    device = result.scalar_one_or_none()
    if device:
        return device  
    device = Device(
        user_id=user_id,
        device_name=device_name
    )
    session.add(device)
    await session.commit()
    await session.refresh(device)
    return device
