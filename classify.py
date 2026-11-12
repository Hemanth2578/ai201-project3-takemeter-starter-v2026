#!/usr/bin/env python3
"""
Label one article with the saved TakeMeter model.

    python classify.py "Harlow Steel cuts 900 jobs as construction slows"

This is the capability the capstone adds: the notebook could only score its
own held-out posts, and this can label text it has never seen. serve.py puts
the same Classifier behind an HTTP endpoint.

The model comes from models/takemeter/, which `python train.py` writes.
"""

import json
import sys
import time
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models" / "takemeter"

# How much of a long text is tokenized to count its tokens. See classify().
HEAD_CHARS = 4096
WORD_MARGIN_TOKENS = 100


class InputError(ValueError):
    """The caller sent something that can't be classified. Their fault, not ours."""


class ModelNotFound(RuntimeError):
    """models/takemeter/ isn't there yet. `python train.py` makes it."""


def validate_text(text):
    """Return the text to classify, or raise InputError saying what was wrong."""
    if text is None:
        raise InputError("'text' is missing")
    if not isinstance(text, str):
        raise InputError(f"'text' must be a string, got {type(text).__name__}")
    if not text.strip():
        raise InputError("'text' is empty")
    return text


def pick_device():
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class Classifier:
    """The saved model, loaded once. classify() is safe to call repeatedly."""

    def __init__(self, model_dir=MODEL_DIR, device=None):
        model_dir = Path(model_dir)
        if not (model_dir / "config.json").exists():
            raise ModelNotFound(
                f"No saved model in {model_dir}. Run `python train.py` first "
                f"(under a minute on a GPU, a few minutes on a CPU)."
            )

        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self._torch = torch
        self.device = device or pick_device()
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
        self.model.to(self.device)
        self.model.eval()

        meta_file = model_dir / "train_meta.json"
        self.meta = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
        # The same token limit the model was trained with. Longer text is cut.
        self.max_length = int(self.meta.get("max_length", 128))
        self.labels = [self.model.config.id2label[i]
                       for i in range(self.model.config.num_labels)]

    def classify(self, text):
        """
        Label one article.

        Returns label, confidence (the winning softmax score), the score for
        every label, how many tokens the text had, whether it was cut to fit,
        and how long the two stages took. For a text over 4,096 characters
        n_tokens is a lower bound, and n_tokens_exact says so.
        """
        text = validate_text(text)
        torch = self._torch

        t0 = time.perf_counter()
        # Counted without truncation so we can say whether the model saw it all.
        #
        # But only the head of a long text is counted. The model reads 128
        # tokens, so tokenizing a 900,000-character article in full (177,274
        # tokens, 758 ms) bought nothing except an exact count. If the head
        # alone overflows the limit by a clear margin, the model's 128 tokens
        # all come from it and the answer is the same as for the full text.
        # The margin is one word's worth: a word is at most 100 word-pieces
        # (longer ones become a single [UNK]), so cutting the head mid-word
        # cannot change anything the model gets to see.
        head = text[:HEAD_CHARS]
        n_tokens = len(self.tokenizer(head, truncation=False, verbose=False)["input_ids"])
        n_tokens_exact = True
        if len(text) > HEAD_CHARS:
            if n_tokens >= self.max_length + WORD_MARGIN_TOKENS:
                text, n_tokens_exact = head, False      # n_tokens is now "at least"
            else:
                # Rare: 4,096 characters that make few tokens (mostly spaces,
                # or one giant unbroken string). Fall back to counting it all.
                n_tokens = len(self.tokenizer(text, truncation=False,
                                              verbose=False)["input_ids"])
        encoded = self.tokenizer(
            text, truncation=True, padding="max_length",
            max_length=self.max_length, return_tensors="pt",
        ).to(self.device)
        t1 = time.perf_counter()

        with torch.no_grad():
            logits = self.model(**encoded).logits[0]
            probs = torch.softmax(logits, dim=-1).cpu().tolist()
        t2 = time.perf_counter()

        best = max(range(len(probs)), key=probs.__getitem__)
        return {
            "label": self.labels[best],
            "confidence": round(probs[best], 4),
            "scores": {label: round(p, 4) for label, p in zip(self.labels, probs)},
            "n_tokens": n_tokens,
            "n_tokens_exact": n_tokens_exact,
            "truncated": n_tokens > self.max_length,
            "timings_ms": {
                "tokenize": round((t1 - t0) * 1000, 2),
                "model": round((t2 - t1) * 1000, 2),
            },
        }


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if len(sys.argv) == 2 else 2
    try:
        classifier = Classifier()
        result = classifier.classify(sys.argv[1])
    except (InputError, ModelNotFound) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
