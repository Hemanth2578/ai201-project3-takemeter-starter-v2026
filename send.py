#!/usr/bin/env python3
"""
Send requests to a running serve.py. A client, so nobody has to fight curl quoting.

    python send.py "Credit Agricole agrees to buy German bank IKB"
    python send.py --held-out 10      # the first 10 posts in test_split.csv
    python send.py --bad              # requests the endpoint should refuse

Start the server first, in another terminal:  python serve.py
"""

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent
DEFAULT_URL = "http://127.0.0.1:8000"

# (what it is, raw request body or None, path). Each should be refused, not crash.
BAD_REQUESTS = [
    ("empty text", b'{"text": ""}', "/classify"),
    ("whitespace only", b'{"text": "   \\n  "}', "/classify"),
    ("no text field", b'{"article": "Fed holds rates"}', "/classify"),
    ("text is a number", b'{"text": 42}', "/classify"),
    ("text is null", b'{"text": null}', "/classify"),
    ("not JSON", b"Fed holds rates steady", "/classify"),
    ("JSON cut short", b'{"text": "Fed holds', "/classify"),
    ("a list, not an object", b'["Fed holds rates"]', "/classify"),
    ("no body", None, "/classify"),
    ("body over 1 MB", b'{"text": "' + b"x" * 1_100_000 + b'"}', "/classify"),
    ("wrong route", b'{"text": "Fed holds rates"}', "/label"),
]


def post(base_url, path, body, timeout=30):
    """POST raw bytes. Returns (http_status, parsed_json_or_text). Never raises on 4xx/5xx."""
    request = urllib.request.Request(
        base_url + path, data=body if body is not None else b"", method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read()
    try:
        return status, json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return status, raw.decode("utf-8", errors="replace")


def classify(base_url, text, timeout=30):
    return post(base_url, "/classify", json.dumps({"text": text}).encode("utf-8"), timeout)


def held_out(n):
    """The first n held-out posts as (text, true_label)."""
    with open(ROOT / "test_split.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [(r["text"], r["label"]) for r in rows[:n]]


def one_line(text, width=60):
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("text", nargs="?", help="one article to classify")
    parser.add_argument("--held-out", type=int, metavar="N",
                        help="send the first N posts from test_split.csv")
    parser.add_argument("--bad", action="store_true",
                        help="send requests the endpoint should refuse")
    parser.add_argument("--url", default=DEFAULT_URL)
    args = parser.parse_args()

    if not (args.text or args.held_out or args.bad):
        parser.print_help()
        return 2

    try:
        if args.text:
            status, body = classify(args.url, args.text)
            print(f"HTTP {status}")
            print(json.dumps(body, indent=2, ensure_ascii=False))

        if args.held_out:
            right = 0
            for text, truth in held_out(args.held_out):
                status, body = classify(args.url, text)
                got = body.get("label") if isinstance(body, dict) else None
                right += got == truth
                print(f"HTTP {status}  {str(got):<15} conf {body.get('confidence', 0):.2f}  "
                      f"{body.get('duration_ms', 0):>7.2f} ms  "
                      f"(true: {truth})  {one_line(text)}")
            print(f"{right} of {args.held_out} match the label in test_split.csv")

        if args.bad:
            for name, body, path in BAD_REQUESTS:
                status, answer = post(args.url, path, body)
                message = answer.get("error") if isinstance(answer, dict) else answer
                print(f"HTTP {status}  {name:<22} -> {message}")

    except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
        print(f"Could not reach {args.url}: {exc}\nIs serve.py running?", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
