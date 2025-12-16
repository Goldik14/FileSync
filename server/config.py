#server/config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/filesync"

STORAGE_PATH = BASE_DIR / "storage" / "files"
STORAGE_PATH.mkdir(parents=True, exist_ok=True)