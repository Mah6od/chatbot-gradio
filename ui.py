from uuid import uuid4
import gradio as gr

from config import USER_AVATAR, BOT_AVATAR
from history import get_sidebar_choices
from chat import (
    handle_undo, handle_retry, handle_like, handle_edit, handle_clear,
    load_conversation, delete_selected, refresh_sidebar,
)

 
def build_ui(respond_fn) -> gr.Blocks:
    with gr.Blocks(title="Local Qwen Chatbot") as demo:

        uuid_state = gr.State(lambda: str(uuid4()))

        with gr.Row():

            # ── Sidebar ───────────────────────────────────────────────────────
            with gr.Column(scale=1, min_width=220):
                gr.Markdown("### 💬 History")

                new_chat_btn = gr.Button("＋ New Chat", variant="primary", size="sm")

                history_list = gr.Radio(
                    choices=get_sidebar_choices(),  # pre-loaded from disk on startup
                    value=None,
                    show_label=False,
                )

                delete_btn = gr.Button("🗑 Delete selected", variant="stop", size="sm")

            # ── Chat area ─────────────────────────────────────────────────────
            with gr.Column(scale=4):
                gr.Markdown("# 🤖 Local Qwen Chatbot\n*Powered by Qwen2.5-0.5B-Instruct*")

                # 1 · Avatars
                chatbot = gr.Chatbot(
                    label="Qwen",
                    avatar_images=(USER_AVATAR, BOT_AVATAR),
                    editable="user",
                    height=500,
                )

                # Send button + file upload + microphone
                textbox = gr.MultimodalTextbox(
                    placeholder="Type a message, attach a file, or record your voice…",
                    show_label=False,
                    file_count="multiple",
                    file_types=["image", "audio", "video", ".pdf", ".txt", ".csv"],
                    sources=["upload", "microphone"],
                    submit_btn="➤",
                )

                chat_iface = gr.ChatInterface(
                    fn=respond_fn,
                    chatbot=chatbot,
                    textbox=textbox,
                    multimodal=True,
                    additional_inputs=[uuid_state],
                    examples=[
                        [{"text": "Hello!", "files": []}, None],
                        [{"text": "What is Python?", "files": []}, None],
                        [{"text": "Tell me a joke", "files": []}, None],
                    ],
                    show_progress="hidden",
                )

        # ── Sidebar events ────────────────────────────────────────────────────
        history_list.change(
            load_conversation,
            inputs=[history_list],
            outputs=[chatbot, uuid_state],
        )

        new_chat_btn.click(
            lambda: ([], str(uuid4()), gr.update(value=None)),
            outputs=[chatbot, uuid_state, history_list],
        )

        delete_btn.click(
            delete_selected,
            inputs=[history_list],
            outputs=[chatbot, uuid_state, history_list],
        )

        chat_iface.chatbot.change(
            refresh_sidebar,
            outputs=[history_list],
        )
        
        chatbot.undo(handle_undo, [chatbot], [chatbot, textbox])
        chatbot.retry(handle_retry(respond_fn), [chatbot], [chatbot])
        chatbot.like(handle_like, None, None)
        chatbot.edit(handle_edit, None, None)
        chatbot.clear(handle_clear, None, [uuid_state, history_list])

    return demo
