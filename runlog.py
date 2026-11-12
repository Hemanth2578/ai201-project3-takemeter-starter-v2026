#!/usr/bin/env python3
"""
The structured run log: one JSON object per line, in logs/classify.jsonl.

serve.py writes a record for every request it answers — the ones it
classified, the ones it rejected, and the ones that broke — plus one when the
server starts and one when it stops. A failure leaves a record like anything
else, so a bad run shows up as a line and not as a gap.

Read it back without writing any code:

    python runlog.py                 # counts and timings for the whole log
    python runlog.py --last 10       # only the 10 most recent requests
    python runlog.py --tail 5        # print the last 5 records as they are

Fields on a request record:

    ts             when it arrived, ISO-8601 UTC, to the millisecond
    request_id     also returned to the caller, so a response can be traced
    event          request | startup | shutdown
    method, path   what was asked for
    status         ok (classified) | rejected (caller's mistake) | error (ours)
    http_status    what the caller was sent
    input_chars    length of the text that came in
    input_preview  its first 160 characters
    n_tokens       how many tokens the text had before any cut
    n_tokens_exact false when the text was over 4,096 characters and only its
                   head was counted, so n_tokens is "at least this many"
    truncated      true if it was longer than the model's 128-token limit
    label          what came out
    confidence     the winning label's score, 0 to 1
    scores         the score for every label
    tokenize_ms    time in the tokenizer
    model_ms       time in the model
    duration_ms    the whole request, from first byte read to response sent
    error          why it was rejected or failed; null when status is ok
"""

import argparse
import json
import statistics
import sys
import threading
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "logs" / "classify.jsonl"


class RunLog:
    """Append-only JSON Lines file. Safe to write from several request threads."""

    def __init__(self, path=LOG_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def write(self, record):
        """
        Append one record. Never raises: a full disk must not turn a request
        that was answered correctly into a 500. Returns True if it was written.
        """
        try:
            line = json.dumps(record, ensure_ascii=False)
            with self._lock, open(self.path, "a", encoding="utf-8", newline="\n") as f:
                f.write(line + "\n")
            return True
        except (OSError, TypeError, ValueError) as exc:
            print(f"[runlog] could not write a record: {exc}", file=sys.stderr)
            return False


def read_records(path=LOG_PATH):
    """Every record in the file, oldest first. A line that isn't JSON is skipped and counted."""
    path = Path(path)
    records, unreadable = [], 0
    if not path.exists():
        return records, unreadable
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                unreadable += 1
    return records, unreadable


def _stats(values):
    values = sorted(values)
    p95 = values[min(len(values) - 1, int(round(0.95 * (len(values) - 1))))]
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "p95": p95,
        "min": values[0],
        "max": values[-1],
    }


def summarise(records):
    """Counts by status, and timings over the requests that were classified."""
    requests = [r for r in records if r.get("event") == "request"]
    classified = [r for r in requests if r.get("status") == "ok" and r.get("label")]

    summary = {
        "requests": len(requests),
        "by_status": {},
        "by_http_status": {},
        "by_label": {},
        "truncated": sum(1 for r in classified if r.get("truncated")),
        "timings_ms": {},
    }
    for r in requests:
        s = str(r.get("status"))
        summary["by_status"][s] = summary["by_status"].get(s, 0) + 1
        h = str(r.get("http_status"))
        summary["by_http_status"][h] = summary["by_http_status"].get(h, 0) + 1
    for r in classified:
        summary["by_label"][r["label"]] = summary["by_label"].get(r["label"], 0) + 1
    for field in ("duration_ms", "tokenize_ms", "model_ms"):
        values = [r[field] for r in classified if isinstance(r.get(field), (int, float))]
        if values:
            summary["timings_ms"][field] = _stats(values)
    return summary


def print_summary(summary):
    print(f"requests: {summary['requests']}")
    for title, key in (("by status", "by_status"), ("by HTTP status", "by_http_status"),
                       ("by label", "by_label")):
        if summary[key]:
            cells = ", ".join(f"{k} {v}" for k, v in sorted(summary[key].items()))
            print(f"  {title}: {cells}")
    n_ok = summary["by_status"].get("ok", 0)
    if summary["timings_ms"]:
        print(f"  cut to fit the token limit: {summary['truncated']}")
        print("\nclassified requests, milliseconds:")
        print(f"  {'':<12} {'n':>4} {'mean':>9} {'median':>9} {'p95':>9} {'min':>9} {'max':>9}")
        for field, s in summary["timings_ms"].items():
            print(f"  {field:<12} {s['n']:>4} {s['mean']:>9.2f} {s['median']:>9.2f} "
                  f"{s['p95']:>9.2f} {s['min']:>9.2f} {s['max']:>9.2f}")
    elif n_ok == 0:
        print("\nNo classified requests in this selection.")


def main():
    parser = argparse.ArgumentParser(description="Summarise the TakeMeter run log.")
    parser.add_argument("--log", default=str(LOG_PATH))
    parser.add_argument("--last", type=int, metavar="N",
                        help="only the N most recent request records")
    parser.add_argument("--tail", type=int, metavar="N",
                        help="print the last N records as JSON and stop")
    args = parser.parse_args()

    records, unreadable = read_records(args.log)
    if not records:
        print(f"No records in {args.log}. Start serve.py and send it a request.")
        return 1
    if unreadable:
        print(f"[note] {unreadable} lines were not valid JSON and were skipped.")

    if args.tail:
        for r in records[-args.tail:]:
            print(json.dumps(r, ensure_ascii=False))
        return 0

    if args.last:
        requests = [r for r in records if r.get("event") == "request"]
        records = requests[-args.last:]
    print(f"{args.log}")
    print_summary(summarise(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
