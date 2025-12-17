# client_gui.py
import sys
import os
import json
import asyncio
import threading
import requests
import websockets
import platform
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QListWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QObject

# ================= CONFIG =================
SERVER_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/"
USERNAME = "stepa"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")
os.makedirs(FILES_DIR, exist_ok=True)

# ================= SIGNALS =================
class UISignals(QObject):
    file_added = Signal(str)
    file_deleted = Signal(str)

signals = UISignals()

# ================= FILE LIST =================
class FileListWidget(QListWidget):
    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            if self.parent_widget:
                self.parent_widget.add_files(files)
            event.acceptProposedAction()
        else:
            event.ignore()

# ================= MAIN WIDGET =================
class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.files = set()
        self.setup_ui()

        signals.file_added.connect(self.on_remote_file_added)
        signals.file_deleted.connect(self.on_remote_file_deleted)

        self.sync_with_server()
        self.start_ws_listener()
        self.register_device()

    def setup_ui(self):
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Добавить файл")
        add_btn.clicked.connect(self.pick_files)
        del_btn = QPushButton("Удалить выбранный")
        del_btn.clicked.connect(self.delete_selected_files)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)

        self.file_list = FileListWidget(parent_widget=self)
        self.file_list.itemDoubleClicked.connect(self.open_file)
        layout.addWidget(QLabel(f"Файлы пользователя: {USERNAME}"))
        layout.addWidget(self.file_list)

        self.setLayout(layout)

    # ---------- File operations ----------
    def pick_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выбор файлов")
        self.add_files(files)

    def add_files(self, paths):
        for path in paths:
            if not os.path.isfile(path):
                continue
            filename = os.path.basename(path)
            if filename in self.files:
                continue

            # Загружаем на сервер
            try:
                with open(path, "rb") as f:
                    requests.post(
                        f"{SERVER_URL}/upload/",
                        headers={"username": USERNAME},
                        files={"file": f},
                        timeout=5
                    )
            except Exception as e:
                print(f"Ошибка загрузки {filename}: {e}")
                continue

            # Локальное сохранение
            local_path = os.path.join(FILES_DIR, filename)
            if not os.path.exists(local_path):
                with open(path, "rb") as src, open(local_path, "wb") as dst:
                    dst.write(src.read())

            self.files.add(filename)
            self.file_list.addItem(filename)

    def delete_selected_files(self):
        selected = self.file_list.selectedItems()
        for item in selected:
            filename = item.text()
            local_path = os.path.join(FILES_DIR, filename)
            if os.path.exists(local_path):
                os.remove(local_path)
            try:
                requests.post(
                    f"{SERVER_URL}/file/delete?filename={filename}",
                    headers={"username": USERNAME},
                    timeout=5
                )
            except Exception as e:
                print(f"Ошибка удаления {filename} на сервере: {e}")

            self.files.discard(filename)
            self.file_list.takeItem(self.file_list.row(item))

    def sync_with_server(self):
        try:
            r = requests.post(
                f"{SERVER_URL}/sync/",
                headers={"username": USERNAME},
                json=list(self.files),
                timeout=5
            )
            missing = r.json().get("missing", [])
            for filename in missing:
                self.download_file(filename)
        except Exception as e:
            print(f"Ошибка sync: {e}")

    def download_file(self, filename):
        path = os.path.join(FILES_DIR, filename)
        try:
            r = requests.get(f"{SERVER_URL}/download/{filename}", timeout=5)
            with open(path, "wb") as f:
                f.write(r.content)
            if filename not in self.files:
                self.files.add(filename)
                self.file_list.addItem(filename)
        except Exception as e:
            print(f"Ошибка скачивания {filename}: {e}")

    # ---------- Remote file events ----------
    def on_remote_file_added(self, filename):
        if filename not in self.files:
            print(f"⬇️ Скачиваем файл: {filename}")
            self.download_file(filename)

    def on_remote_file_deleted(self, filename):
        if filename in self.files:
            local_path = os.path.join(FILES_DIR, filename)
            if os.path.exists(local_path):
                os.remove(local_path)
            self.files.discard(filename)
            for i in range(self.file_list.count()-1, -1, -1):
                if self.file_list.item(i).text() == filename:
                    self.file_list.takeItem(i)
                    break

    # ---------- Open file ----------
    def open_file(self, item):
        import subprocess
        filename = item.text()
        path = os.path.join(FILES_DIR, filename)
        if os.path.exists(path):
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        else:
            QMessageBox.warning(self, "Ошибка", f"Файл {filename} не найден")

    # ---------- Device registration ----------
    def register_device(self):
        hostname = platform.node()
        os_name = platform.system()
        os_version = platform.release()
        device_name = f"{hostname} | {os_name} {os_version}"
        try:
            requests.post(
                f"{SERVER_URL}/devices/register",
                headers={"username": USERNAME},
                params={"device_name": device_name},
                timeout=5
            )
        except Exception as e:
            print(f"Ошибка регистрации устройства: {e}")

    # ---------- WebSocket ----------
    def start_ws_listener(self):
        threading.Thread(target=self.ws_thread, daemon=True).start()

    def ws_thread(self):
        asyncio.run(self.ws_loop())

    async def ws_loop(self):
        while True:
            try:
                async with websockets.connect(WS_URL) as ws:
                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        action = data.get("action")
                        filename = data.get("filename")
                        if action == "delete" and filename:
                            signals.file_deleted.emit(filename)
                        elif action == "add" and filename:
                            signals.file_added.emit(filename)
            except:
                await asyncio.sleep(2)

# ================= MAIN WINDOW =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileSync")
        self.resize(600, 400)
        self.setCentralWidget(MainWidget())

# ================= RUN ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())