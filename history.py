import json
from pathlib import Path
from datetime import datetime
from config import HISTORY_FILE


def load_all() -> dict:
    """Load every saved conversation from disk. Returns {session_id: entry}."""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            pass
    return {}


def _write_all(data: dict):
    HISTORY_FILE.write_text(json.dumps(data, indent=2))


def save_conversation(session_id: str, history: list):
    """Persist a single conversation. Skips non-text (file/audio) messages."""
    storable = []
    for msg in history:
        content = msg.get("content", "")
        if isinstance(content, str) and content:
            storable.append({"role": msg["role"], "content": content})

    if not storable:
        return

    first_user = next(
        (m["content"] for m in storable if m["role"] == "user"), "Conversation"
    )
    title = first_user[:40] + ("…" if len(first_user) > 40 else "")

    all_history = load_all()
    all_history[str(session_id)] = {
        "title": title,
        "messages": storable,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    _write_all(all_history)


def delete_conversation(session_id: str):
    """Remove a conversation from disk."""
    all_history = load_all()
    all_history.pop(str(session_id), None)
    _write_all(all_history)


def get_sidebar_choices() -> list[tuple[str, str]]:
    """Return [(title, session_id), ...] sorted newest-first for the sidebar."""
    all_history = load_all()
    sorted_items = sorted(
        all_history.items(),
        key=lambda x: x[1].get("updated_at", ""),
        reverse=True,
    )
    return [(v.get("title", sid), sid) for sid, v in sorted_items]


def get_messages(session_id: str) -> list:
    """Return the stored messages for a given session_id (or [] if not found)."""
    return load_all().get(str(session_id), {}).get("messages", [])
