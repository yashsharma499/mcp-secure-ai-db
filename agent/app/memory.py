import json
import os
import threading
from typing import Optional

from app.config import get_settings
from app.schemas import MemoryState


_lock = threading.Lock()


class MemoryStore:
    def __init__(self):
        self._settings = get_settings()
        self._path = self._settings.memory_store_path
        self._ensure_store()

    def _ensure_store(self):
        directory = os.path.dirname(self._path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self._path):
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_all(self) -> dict:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_all(self, data: dict):
        tmp_path = f"{self._path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp_path, self._path)

    def get(self, conversation_key: str) -> MemoryState:
        if not conversation_key:
            return MemoryState()

        with _lock:
            data = self._load_all()
            raw = data.get(conversation_key)
            if not raw:
                return MemoryState()
            try:
                return MemoryState(**raw)
            except Exception:
                return MemoryState()

    def set(self, conversation_key: str, state: MemoryState):
        if not conversation_key:
            return

        with _lock:
            data = self._load_all()
            data[conversation_key] = state.model_dump()
            self._save_all(data)

    def clear(self, conversation_key: str):
        if not conversation_key:
            return

        with _lock:
            data = self._load_all()
            if conversation_key in data:
                del data[conversation_key]
                self._save_all(data)


memory_store = MemoryStore()
