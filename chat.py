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
    ...

def handle_edit(edit_data: gr.EditData):
    ...

def handle_clear():
    ...

def load_conversation(selected_sid: str):
    ...

def delete_selected(selected_sid: str):
    ...

def refresh_sideber():
    ...