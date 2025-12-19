#client/client_gui.py
import sys
import os
import json
import asyncio
import threading
import requests
import websockets
import platform
import subprocess

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QListWidget, QMessageBox,
<<<<<<< HEAD
    QLineEdit
=======
    QLineEdit, QFrame, QListWidgetItem
>>>>>>> rework-auth
)
from PySide6.QtCore import Signal, QObject, Qt

# ================= CONFIG =================
SERVER_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")
os.makedirs(FILES_DIR, exist_ok=True)

# ================= GLOBAL STATE =================
class AppState:
    token: str | None = None
    username: str | None = None

state = AppState()

# ================= SIGNALS =================
class UISignals(QObject):
    file_added = Signal(str)
    file_deleted = Signal(str)

signals = UISignals()

# ================= LOGIN WIDGET =================
class LoginWidget(QWidget):
    def __init__(self, on_success):
<<<<<<< HEAD
        super().__init__()
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Логин"))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Пароль"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        btn_login = QPushButton("Войти")
        btn_register = QPushButton("Регистрация")
        btn_login.clicked.connect(self.login)
        btn_register.clicked.connect(self.register)
        layout.addWidget(btn_login)
        layout.addWidget(btn_register)
        self.setLayout(layout)

    def login(self):
        try:
            r = requests.post(
                f"{SERVER_URL}/auth/login",
                params={
                    "username": self.username.text(),
                    "password": self.password.text()
                },
                timeout=5
            )
            r.raise_for_status()
            data = r.json()
            state.token = data["access_token"]
            state.username = data.get("username", self.username.text())
            self.on_success()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def register(self):
        try:
            r = requests.post(
                f"{SERVER_URL}/auth/register",
                params={
                    "username": self.username.text(),
                    "password": self.password.text()
                },
                timeout=5
            )
            r.raise_for_status()
            QMessageBox.information(self, "OK", "Пользователь создан")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

# ================= FILE LIST =================
class FileListWidget(QListWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DropOnly)  # для DnD
        self.itemDoubleClicked.connect(self.parent.open_file)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        files = [u.toLocalFile() for u in e.mimeData().urls() if os.path.isfile(u.toLocalFile())]
        self.parent.add_files(files)

# ================= FILES WIDGET =================
class FilesWidget(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout
        self.files = {}    # {filename: size}
        self.devices = {}  # {device_name: online}
        self.ws_task = None

        # создаём папку для текущего пользователя
        self.user_dir = os.path.join(FILES_DIR, state.username)
        os.makedirs(self.user_dir, exist_ok=True)

        self.setup_ui()
        signals.file_added.connect(self.on_remote_add)
        signals.file_deleted.connect(self.on_remote_delete)
        self.register_device()
        self.sync()
        self.start_ws()

    def setup_ui(self):
        main_layout = QHBoxLayout()  # горизонтально: слева файлы, справа устройства

        # ---------- Список файлов ----------
        left_layout = QVBoxLayout()
        self.header = QLabel(f"Пользователь: {state.username}")
        left_layout.addWidget(self.header)

        btns = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        del_btn = QPushButton("Удалить")
        logout_btn = QPushButton("Выйти")
        add_btn.clicked.connect(self.pick_files)
        del_btn.clicked.connect(self.delete_selected)
        logout_btn.clicked.connect(self.logout)
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        btns.addWidget(logout_btn)
        left_layout.addLayout(btns)

        self.list = FileListWidget(self)
        left_layout.addWidget(self.list)
        main_layout.addLayout(left_layout, 3)

        # ---------- Список устройств ----------
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Устройства:"))
        self.devices_list = QListWidget()
        right_layout.addWidget(self.devices_list)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)
=======
        super().__init__()
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Логин"))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Пароль"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        btn_login = QPushButton("Войти")
        btn_register = QPushButton("Регистрация")

        btn_login.clicked.connect(self.login)
        btn_register.clicked.connect(self.register)

        layout.addWidget(btn_login)
        layout.addWidget(btn_register)

        self.setLayout(layout)

    # ✅ ВОТ ЭТОГО НЕ ХВАТАЛО
    def login(self):
        try:
            r = requests.post(
                f"{SERVER_URL}/auth/login",
                params={
                    "username": self.username.text(),
                    "password": self.password.text()
                },
                timeout=5
            )
            r.raise_for_status()
            data = r.json()
            state.token = data["access_token"]
            state.username = data.get("username", self.username.text())
            self.on_success()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def register(self):
        try:
            r = requests.post(
                f"{SERVER_URL}/auth/register",
                params={
                    "username": self.username.text(),
                    "password": self.password.text()
                },
                timeout=5
            )
            r.raise_for_status()
            QMessageBox.information(self, "OK", "Пользователь создан")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

# ================= FILE LIST =================
class FileListWidget(QListWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DropOnly)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                files.append(path)

        if files:
            self.parent.add_files(files)

        event.acceptProposedAction()

# ================= FILES WIDGET =================
class FilesWidget(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout
        self.files = {}    # {filename: size}
        self.devices = {}  # {device_name: online}
        self.ws_task = None
        # создаём папку для текущего пользователя
        self.user_dir = os.path.join(FILES_DIR, state.username)
        os.makedirs(self.user_dir, exist_ok=True)

        self.setup_ui()
        signals.file_added.connect(self.on_remote_add)
        signals.file_deleted.connect(self.on_remote_delete)
        self.register_device()
        self.sync()
        self.start_ws()

    def setup_ui(self):
        root = QVBoxLayout()
        root.setSpacing(8)

        # ====== ВЕРХНЯЯ ПАНЕЛЬ КНОПОК ======
        buttons = QHBoxLayout()

        add_btn = QPushButton("Добавить")
        del_btn = QPushButton("Удалить")
        logout_btn = QPushButton("Выход")

        add_btn.clicked.connect(self.pick_files)
        del_btn.clicked.connect(self.delete_selected)
        logout_btn.clicked.connect(self.logout)

        buttons.addWidget(add_btn)
        buttons.addWidget(del_btn)
        buttons.addStretch()
        buttons.addWidget(logout_btn)

        root.addLayout(buttons)

        # ====== РАЗДЕЛИТЕЛЬ ======
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        root.addWidget(line1)

        # ====== ПОЛЬЗОВАТЕЛЬ ======
        self.header = QLabel(f"Пользователь: {state.username}")
        self.header.setStyleSheet("font-weight: bold;")
        root.addWidget(self.header)

        # ====== РАЗДЕЛИТЕЛЬ ======
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        root.addWidget(line2)

        # ====== ДВА ОКНА: ФАЙЛЫ / УСТРОЙСТВА ======
        split = QHBoxLayout()
        split.setSpacing(10)

        # --- ФАЙЛЫ ---
        files_layout = QVBoxLayout()
        files_label = QLabel("ФАЙЛЫ")
        files_label.setAlignment(Qt.AlignCenter)
        files_label.setStyleSheet("font-weight: bold;")

        self.list = FileListWidget(self)
        self.list.itemDoubleClicked.connect(self.open_file)

        files_layout.addWidget(files_label)
        files_layout.addWidget(self.list)

        # --- УСТРОЙСТВА ---
        devices_layout = QVBoxLayout()
        devices_label = QLabel("УСТРОЙСТВА")
        devices_label.setAlignment(Qt.AlignCenter)
        devices_label.setStyleSheet("font-weight: bold;")

        self.devices_list = QListWidget()

        devices_layout.addWidget(devices_label)
        devices_layout.addWidget(self.devices_list)

        split.addLayout(files_layout, 1)
        split.addLayout(devices_layout, 1)

        root.addLayout(split)

        self.setLayout(root)
>>>>>>> rework-auth

    # ---------- AUTH HEADER ----------
    def headers(self):
        return {"Authorization": f"Bearer {state.token}"}

    # ---------- FILE OPS ----------
    def pick_files(self):
        files, _ = QFileDialog.getOpenFileNames(self)
        self.add_files(files)

    def add_files(self, paths):
        for path in paths:
            name = os.path.basename(path)
            if name in self.files:
                continue
            size = os.path.getsize(path)
            try:
                with open(path, "rb") as f:
                    requests.post(
                        f"{SERVER_URL}/upload/",
                        headers=self.headers(),
                        files={"file": f}
                    )
                local = os.path.join(self.user_dir, name)
                if not os.path.exists(local):
                    with open(path, "rb") as s, open(local, "wb") as d:
                        d.write(s.read())
                self.files[name] = size
<<<<<<< HEAD
                self.list.addItem(f"{name} ({self.format_size(size)})")
=======
                item = QListWidgetItem(f"{name} ({self.format_size(size)})")
                item.setData(Qt.UserRole, name)
                self.list.addItem(item)
>>>>>>> rework-auth
            except Exception as e:
                print(f"Ошибка добавления файла {name}: {e}")

    def delete_selected(self):
        for item in self.list.selectedItems():
<<<<<<< HEAD
            name = item.text().split(" (")[0]
=======
            name = item.data(Qt.UserRole)
>>>>>>> rework-auth
            try:
                requests.post(
                    f"{SERVER_URL}/file/delete",
                    headers=self.headers(),
                    params={"filename": name}
                )
            except Exception as e:
                print(f"Ошибка удаления на сервере {name}: {e}")
            path = os.path.join(self.user_dir, name)
            if os.path.exists(path):
                os.remove(path)
            self.files.pop(name, None)
            self.list.takeItem(self.list.row(item))

    def sync(self):
        try:
            r = requests.post(
                f"{SERVER_URL}/sync/",
                headers=self.headers(),
                json=list(self.files.keys())
            )
            for name in r.json().get("missing", []):
                self.download(name)
        except Exception as e:
            print(f"Ошибка sync: {e}")

    def download(self, name):
        try:
            r = requests.get(f"{SERVER_URL}/download/{name}", headers=self.headers())
            local = os.path.join(self.user_dir, name)
            with open(local, "wb") as f:
                f.write(r.content)
            size = os.path.getsize(local)
            self.files[name] = size
<<<<<<< HEAD
            self.list.addItem(f"{name} ({self.format_size(size)})")
=======
            item = QListWidgetItem(f"{name} ({self.format_size(size)})")
            item.setData(Qt.UserRole, name)
            self.list.addItem(item)
>>>>>>> rework-auth
        except Exception as e:
            print(f"Ошибка download {name}: {e}")

    def format_size(self, size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    # ---------- WS ----------
    def start_ws(self):
        threading.Thread(target=self.ws_thread, daemon=True).start()

    def ws_thread(self):
        asyncio.run(self.ws_loop())

    async def ws_loop(self):
        url = f"{WS_URL}?token={state.token}"
        while True:
            try:
                async with websockets.connect(url) as ws:
                    while True:
                        data = json.loads(await ws.recv())
                        action = data.get("action")
                        filename = data.get("filename")
                        device = data.get("device")
<<<<<<< HEAD
                        # Фильтруем по пользователю
                        if data.get("user_id") != state.username:
                            continue
=======
>>>>>>> rework-auth
                        if action == "add" and filename:
                            signals.file_added.emit(filename)
                        elif action == "delete" and filename:
                            signals.file_deleted.emit(filename)
                        elif action == "device" and device:
                            self.devices[device["name"]] = device["online"]
                            self.update_devices_list()
            except:
                await asyncio.sleep(2)

    def update_devices_list(self):
        self.devices_list.clear()
        for dev, online in self.devices.items():
            status = "онлайн" if online else "офлайн"
            self.devices_list.addItem(f"{dev}: {status}")

    # ---------- REMOTE EVENTS ----------
    def on_remote_add(self, name):
        if name not in self.files:
            self.download(name)

    def on_remote_delete(self, name):
        if name in self.files:
            self.files.pop(name, None)
            for i in range(self.list.count()):
<<<<<<< HEAD
                if self.list.item(i).text().startswith(name):
=======
                item = self.list.item(i)
                if item.data(Qt.UserRole) == name:
>>>>>>> rework-auth
                    self.list.takeItem(i)
                    break
            path = os.path.join(self.user_dir, name)
            if os.path.exists(path):
                os.remove(path)

    # ---------- DEVICE ----------
    def register_device(self):
        try:
            device = f"{platform.node()} | {platform.system()} {platform.release()}"
            requests.post(
                f"{SERVER_URL}/devices/register",
                headers=self.headers(),
                params={"device_name": device}
            )
            self.devices[device] = True
            self.update_devices_list()
        except Exception as e:
            print(f"Ошибка регистрации устройства: {e}")

    # ---------- OPEN FILE ----------
    def open_file(self, item):
<<<<<<< HEAD
        name = item.text().split(" (")[0]
=======
        name = item.data(Qt.UserRole)
>>>>>>> rework-auth
        path = os.path.join(self.user_dir, name)
        if not os.path.exists(path):
            QMessageBox.warning(self, "Ошибка", f"Файл {name} не найден")
            return
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    # ---------- LOGOUT ----------
    def logout(self):
        state.token = None
        state.username = None
        self.on_logout()

# ================= MAIN WINDOW =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileSync")
        self.resize(600, 400)
        self.show_login()

    def show_login(self):
        self.setCentralWidget(LoginWidget(self.show_files))

    def show_files(self):
        self.setCentralWidget(FilesWidget(self.show_login))

# ================= RUN =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
