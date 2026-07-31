from uuid import uuid4
from pathlib import Path
import gradio as gr

from model import stream_response
from history import (
    save_conversation, delete_conversation,
    get_sidebar_choices, get_messages
)

def build_messages(history: list, user_text: str) -> list:
    ...

def respond(tokenizer, model, device):
    ...

def handle_retry(respond_fn):
    ...

def handle_like(data: gr.LikeData):
    print(f"[Like] {'👍' if data.liked else '👎'}")

def handle_edit(edit_data: gr.EditData):
    print(f"[Edit] index={edit_data.index}, value={edit_data.value}")

def handle_clear():
    new_uuid = str(uuid4())
    print(f"[Clear] new session: {new_uuid}")
    return new_uuid, gr.update(choices=get_sidebar_choices(), value=None)

def handle_undo(history, undo_data: gr.UndoData):
    print(f"[Undo] index={undo_data.index}")
    return history[:undo_data.index], undo_data.value

def refresh_sideber():
    return gr.update(choices=get_sidebar_choices())

# ── Sidebar handlers ──────────────────────────────────────────────────────────
def load_conversation(selected_sid: str):
    if not selected_sid:
        return [], str(uuid4())
    messages = get_messages(selected_sid)
    print(f"[Load] session={selected_sid}, {len(messages)} messages")
    return messages, selected_sid

def delete_selected(selected_sid: str):
    if selected_sid:
        delete_conversation(selected_sid)
        print(f"[Delete] session={selected_sid}")
    return [], str(uuid4()), gr.update(choices=get_sidebar_choices(), value=None)