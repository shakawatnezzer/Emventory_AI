import tensorflow as tf
import numpy as np
from transformers import BertTokenizer
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent / "models" / "intent_model_zip"
MAX_LEN = 64

INTENT_LABELS = [
    "search_running_shoes",
    "gym_shoes",
    "casual_shoes"
]

tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")

infer = None  


def load_model():
    global infer
    if infer is None:
        model = tf.saved_model.load(str(MODEL_PATH))
        infer = model.signatures["serving_default"]
        print("✅ ML model loaded")


def tokenize(text: str):
    enc = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=MAX_LEN,
        return_tensors="tf"
    )
    return {
        "input_ids": enc["input_ids"],
        "attention_mask": enc["attention_mask"]
    }


def predict_intent(text: str):
    if infer is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    
    inputs = tokenize(text)
    outputs = infer(**inputs)
    logits = list(outputs.values())[0]
    probs = tf.nn.softmax(logits, axis=-1).numpy()[0]
    idx = int(np.argmax(probs))
    return INTENT_LABELS[idx], float(probs[idx])
