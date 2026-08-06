from uuid import uuid4
from pathlib import Path
import gradio as gr

from model import stream_response
from history import save_conversation, delete_conversation, get_sidebar_choices, get_messages


def build_messages(history: list, user_text: str) -> list:
    """Convert Gradio history + current prompt into OpenAI-style message list."""
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for entry in history:
        role    = entry.get("role")
        content = entry.get("content")
        if role in ("user", "assistant"):
            if isinstance(content, list):
                # multimodal content block → extract text parts only
                content = " ".join(
                    c.get("text", "") for c in content
                    if isinstance(c, dict) and c.get("type") == "text"
                )
            if content:
                messages.append({"role": role, "content": str(content)})
    messages.append({"role": "user", "content": user_text})
    return messages

# ── Main streaming respond ────────────────────────────────────────────────────
def respond(tokenizer, model, device):
    def _respond(message: dict, history: list, session_id: str):
        user_text  = message.get("text") or ""
        user_files = message.get("files") or []

        if user_files:
            file_names = ", ".join(Path(f).name for f in user_files)
            print(f"[Files received] {file_names}")
            if not user_text:
                user_text = f"[User sent {len(user_files)} file(s): {file_names}]"

        messages = build_messages(history, user_text)

        partial = ""
        for partial in stream_response(tokenizer, model, device, messages):
            yield partial

        # Persist after the full reply is assembled
        full_history = history + [
            {"role": "user",      "content": user_text},
            {"role": "assistant", "content": partial},
        ]
        save_conversation(session_id, full_history)

    return _respond


# ── Event handlers ────────────────────────────────────────────────────────────
def handle_undo(history, undo_data: gr.UndoData):
    print(f"[Undo] index={undo_data.index}")
    return history[:undo_data.index], undo_data.value


def handle_retry(respond_fn):
    """Returns a retry handler pre-bound to the respond function."""
    def _retry(history, retry_data: gr.RetryData):
        print(f"[Retry] prompt={retry_data.value!r}")
        yield from respond_fn(
            {"text": retry_data.value, "files": []},
            history[:retry_data.index],
            "retry",
        )
    return _retry


def handle_like(data: gr.LikeData):
    print(f"[Like] {'👍' if data.liked else '👎'} {data.value!r}")


def handle_edit(edit_data: gr.EditData):
    print(f"[Edit] index={edit_data.index}, value={edit_data.value!r}")


def handle_clear():
    new_uuid = str(uuid4())
    print(f"[Clear] new session: {new_uuid}")
    return new_uuid, gr.update(choices=get_sidebar_choices(), value=None)


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


def refresh_sidebar():
    return gr.update(choices=get_sidebar_choices())
