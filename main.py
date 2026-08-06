from model import load_model
from chat import respond
from ui import build_ui

if __name__ == "__main__":
    tokenizer, model, device = load_model()
    respond_fn = respond(tokenizer, model, device)
    demo = build_ui(respond_fn)
    demo.launch()