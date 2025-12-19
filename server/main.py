#server/main.py
from fastapi import FastAPI
from server.api import upload, download, sync, websocket, devices, file_delete, auth
<<<<<<< HEAD
from server.db.database import engine
from server.db.models import Base
=======
>>>>>>> rework-auth

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(upload.router)
app.include_router(download.router)
app.include_router(sync.router)
app.include_router(websocket.router)
app.include_router(devices.router)
app.include_router(file_delete.router)
app.include_router(auth.router)