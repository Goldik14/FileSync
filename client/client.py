#client/client.py
import os
import requests
from config import SERVER_URL, FILES_DIR

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(BASE_DIR, FILES_DIR)
os.makedirs(FILES_PATH, exist_ok=True)

def list_local_files():
    return os.listdir(FILES_PATH)

def upload_file(filename):
    path = os.path.join(FILES_PATH, filename)
    if not os.path.exists(path):
        print(f"Файл {filename} не найден в {FILES_PATH}")
        return
    with open(path, "rb") as f:
        r = requests.post(f"{SERVER_URL}/upload/", files={"file": f})
        try:
            print(r.json())
        except Exception:
            print("Сервер вернул не JSON:", r.text)

def download_file(filename):
    r = requests.get(f"{SERVER_URL}/download/{filename}")
    path = os.path.join(FILES_PATH, filename)
    with open(path, "wb") as f:
        f.write(r.content)

def sync():
    r = requests.post(f"{SERVER_URL}/sync/", json=list_local_files())
    for filename in r.json()["missing"]:
        download_file(filename)

if __name__ == "__main__":
    sync()