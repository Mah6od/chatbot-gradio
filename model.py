import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from threading import Thread
from config import MODEL_PATH, MAX_NEW_TOKENS, TEMPERATURE, TOP_P

def get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"

def load_model():
    device = get_device()
    print(f"Loading model on {device}...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.float16 if device != "cpu" else torch.float32,
        device_map=device,
    )
    model.eval()
    print("Model ready!")
    return tokenizer, model, device


def stream_response(tokenizer, model, device, messages: list):
    """
    Generator that streams decoded tokens one by one.
    `messages` is a fully-built OpenAI-style list (system + history + user).
    """
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(device)

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    thread = Thread(target=model.generate, kwargs=dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        pad_token_id=tokenizer.eos_token_id,
    ))
    thread.start()

    partial = ""
    for token in streamer:
        partial += token
        yield partial

    thread.join()
