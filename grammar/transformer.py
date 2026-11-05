"""Transformer layer: contextual correction with a T5 grammar-error-correction model."""
from functools import lru_cache

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "prithivida/grammar_error_correcter_v1"


@lru_cache(maxsize=1)
def _load():
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    model.eval()
    return tok, model


def correct(sentence: str, num_beams: int = 5, max_length: int = 128) -> str:
    tok, model = _load()
    inputs = tok("gec: " + sentence, return_tensors="pt", truncation=True, max_length=max_length)
    out = model.generate(**inputs, num_beams=num_beams, max_length=max_length, early_stopping=True)
    return tok.decode(out[0], skip_special_tokens=True).strip()
