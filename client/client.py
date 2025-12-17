#client/client.py
import os
import requests
import asyncio
import websockets
import json
from config import SERVER_URL, FILES_DIR, WS_URL

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
    path = os.path.join(FILES_PATH, filename)
    r = requests.get(f"{SERVER_URL}/download/{filename}")
    with open(path, "wb") as f:
        f.write(r.content)
    print(f"Файл {filename} скачан")

def sync():
    r = requests.post(f"{SERVER_URL}/sync/", json=list_local_files())
    for filename in r.json()["missing"]:
        download_file(filename)

async def ws_listener():
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                print("WebSocket подключен")
                sync()
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    filename = data.get("filename")

                    if filename and filename not in list_local_files():
                        print(f"Новое уведомление: {filename}")
                        download_file(filename)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket отключён, переподключение через 2 сек...")
            await asyncio.sleep(2)
        except Exception as e:
            print("Ошибка WebSocket:", e)
            await asyncio.sleep(5)

async def main():
    upload_file("Wiz Khalifa - Black and Yellow.mp3")
    sync()
    await ws_listener()

if __name__ == "__main__":
    asyncio.run(main())