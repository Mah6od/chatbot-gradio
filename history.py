import json
from pathlib import Path
from datetime import datetime
from config import HISTORY_FILE

def load_all() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            pass
    return {}

def save_conversation(session_id: str, history: list):
    ...

def delete_conversation(session_id: str):
    ...

def get_sidebar_choices():
    ...

def get_messages(session_id: str) -> list:
    ...