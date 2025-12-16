#server/main.py
from fastapi import FastAPI
from server.api import upload, download, sync

app = FastAPI()

app.include_router(upload.router)
app.include_router(download.router)
app.include_router(sync.router)