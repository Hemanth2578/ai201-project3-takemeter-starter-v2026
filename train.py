#!/usr/bin/env python3
"""
Train the TakeMeter classifier once and SAVE it, so it can be served.

    python train.py

The notebook (takemeter.ipynb) trains the same model but throws it away when
the kernel stops. This script repeats the notebook's seed-42 run with the same
data, split and settings, then writes the model to models/takemeter/ where
classify.py and serve.py load it from.

Nothing here changes the experiment. The split, the training arguments and the
scoring are the notebook's sections 3-5. It does NOT overwrite results.json or
test_split.csv: those are the unit 5/6 evidence. It only reads them, to check
that the model it just saved is the one they describe.
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    set_seed,
)

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models" / "takemeter"

# ── The notebook's settings, unchanged (section 2) ──────────────────────────
LABELS = ["Business", "Economy", "Administrative", "None of These"]
BASE_MODEL = "distilbert-base-uncased"
EPOCHS = 10
LEARNING_RATE = 2e-5
BATCH_SIZE = 16
MAX_LENGTH = 128
SEED = 42


def pick_device():
    if torch.cuda.is_available():
        return "cuda", torch.cuda.get_device_name(0)
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps", "Apple Silicon GPU (MPS)"
    return "cpu", "CPU"


def split_dataset(df, seed, test_size=0.15, val_size=0.15):
    """Stratified 70/15/15 — the notebook's section 3, line for line."""
    def _stratify_on(frame):
        counts = frame["label"].value_counts()
        return frame["label"] if counts.min() >= 2 else None

    rest, test = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=_stratify_on(df)
    )
    val_share = val_size / (1 - test_size)
    train, val = train_test_split(
        rest, test_size=val_share, random_state=seed, stratify=_stratify_on(rest)
    )
    return (
        train.reset_index(drop=True),
        val.reset_index(drop=True),
        test.reset_index(drop=True),
    )


def to_ids(df, labels):
    lookup = {label: i for i, label in enumerate(labels)}
    out = df.copy()
    out["labels"] = out["label"].astype(str).str.strip().map(lookup)
    return out[["text", "labels"]]


def compute_metrics(eval_pred):
    logits, gold = eval_pred
    predicted = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(gold, predicted),
        "f1_macro": f1_score(gold, predicted, average="macro", zero_division=0),
    }


def train_model(train_df, val_df, labels, seed):
    """Fine-tune — the notebook's section 4. Returns (trainer, tokenizer)."""
    set_seed(seed)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=len(labels),
        id2label={i: l for i, l in enumerate(labels)},
        label2id={l: i for i, l in enumerate(labels)},
    )

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, padding="max_length",
                         max_length=MAX_LENGTH)

    train_ds = Dataset.from_pandas(to_ids(train_df, labels)).map(tokenize, batched=True)
    val_ds = Dataset.from_pandas(to_ids(val_df, labels)).map(tokenize, batched=True)

    args = TrainingArguments(
        output_dir=str(ROOT / "takemeter_out"),
        num_train_epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=10,
        seed=seed,
        report_to="none",
        disable_tqdm=True,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    return trainer, tokenizer


def evaluate(trainer, tokenizer, test_df, labels):
    """Score on the held-out split — the notebook's section 5, trimmed."""
    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, padding="max_length",
                         max_length=MAX_LENGTH)

    test_ds = Dataset.from_pandas(to_ids(test_df, labels)).map(tokenize, batched=True)
    output = trainer.predict(test_ds)
    predicted = np.argmax(output.predictions, axis=-1)
    gold = np.array(output.label_ids)

    _, recall, f1, support = precision_recall_fscore_support(
        gold, predicted, labels=list(range(len(labels))), zero_division=0
    )
    return {
        "n_test": int(len(gold)),
        "accuracy": float(accuracy_score(gold, predicted)),
        "f1_macro": float(f1_score(gold, predicted, average="macro", zero_division=0)),
        "per_label": {
            label: {"recall": float(recall[i]), "f1": float(f1[i]),
                    "support": int(support[i])}
            for i, label in enumerate(labels)
        },
    }


def check_against_unit6(test_df, scores):
    """Is the model just saved the one results.json describes? Report, don't fix."""
    split_file, results_file = ROOT / "test_split.csv", ROOT / "results.json"

    if split_file.exists():
        committed = pd.read_csv(split_file)["text"].tolist()
        same = committed == test_df["text"].tolist()
        print(f"[{'ok' if same else 'DIFFERENT'}] held-out split vs test_split.csv "
              f"({len(test_df)} posts)")
    if results_file.exists():
        before = json.loads(results_file.read_text(encoding="utf-8"))
        gap = scores["accuracy"] - before["accuracy"]
        print(f"[{'ok' if abs(gap) < 1e-9 else 'DIFFERENT'}] accuracy {scores['accuracy']:.3f} "
              f"vs results.json {before['accuracy']:.3f}  (gap {gap:+.3f})")
        if abs(gap) >= 1e-9:
            print("     Different hardware does the arithmetic in a different order, so a")
            print("     small gap is expected off the machine results.json was written on.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", default=str(MODEL_DIR),
                        help="where to save the model (default: models/takemeter)")
    args = parser.parse_args()
    out_dir = Path(args.out)

    csv = ROOT / "labels.csv"
    if not csv.exists():
        print(f"labels.csv not found in {ROOT}. Run this from inside the repo.")
        return 1

    device, device_name = pick_device()
    df = pd.read_csv(csv)
    train_df, val_df, test_df = split_dataset(df, SEED)
    print(f"device: {device} ({device_name})")
    print(f"labels.csv: {len(df)} rows  ->  train {len(train_df)} · val {len(val_df)} "
          f"· test {len(test_df)}")
    print(f"seed {SEED}, {EPOCHS} epochs, lr {LEARNING_RATE}, batch {BATCH_SIZE}\n")

    started = time.perf_counter()
    trainer, tokenizer = train_model(train_df, val_df, LABELS, SEED)
    train_seconds = time.perf_counter() - started

    scores = evaluate(trainer, tokenizer, test_df, LABELS)

    out_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))

    meta = {
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_model": BASE_MODEL,
        "labels": LABELS,
        "seed": SEED,
        "epochs": EPOCHS,
        "learning_rate": LEARNING_RATE,
        "batch_size": BATCH_SIZE,
        "max_length": MAX_LENGTH,
        "n_train": int(len(train_df)),
        "train_seconds": round(train_seconds, 1),
        "device": device,
        "device_name": device_name,
        "torch_version": torch.__version__,
        **scores,
    }
    (out_dir / "train_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    size_mb = sum(p.stat().st_size for p in out_dir.rglob("*") if p.is_file()) / 1e6
    print(f"\nTrained in {train_seconds:.0f}s.")
    print(f"accuracy {scores['accuracy']:.3f}   macro F1 {scores['f1_macro']:.3f}")
    for label, s in scores["per_label"].items():
        print(f"  {label:<16} recall {s['recall']:.3f}   F1 {s['f1']:.3f}   (n={s['support']})")
    print()
    check_against_unit6(test_df, scores)
    print(f"\nSaved to {out_dir}  ({size_mb:.0f} MB). This folder is in .gitignore.")
    print("Next: python serve.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
