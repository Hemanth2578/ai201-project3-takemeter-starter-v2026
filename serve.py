#!/usr/bin/env python3
"""
Serve the TakeMeter classifier over HTTP.

    python serve.py

Then, from another terminal:

    curl -X POST http://127.0.0.1:8000/classify \
         -H "Content-Type: application/json" \
         -d '{"text": "Credit Agricole agrees to buy German bank IKB"}'

Two routes:

    POST /classify   {"text": "<one article>"}  ->  a label and a confidence
    GET  /health     is the model loaded, and which one

Standard library only (http.server), so there is nothing new to install. The
model is loaded once at start-up from models/takemeter/, which `python
train.py` writes.

What a caller gets back:

    200  a label                       the text was classified
    400  {"error": ...}                the request was the caller's mistake
    404  {"error": ...}                no such route
    413  {"error": ...}                body over 1 MB
    500  {"error": ...}                the model failed; our mistake

Every one of those writes a record to logs/classify.jsonl (see runlog.py).
"""

import argparse
import json
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from classify import MODEL_DIR, Classifier, InputError, ModelNotFound
from runlog import LOG_PATH, RunLog

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
MAX_BODY_BYTES = 1_000_000      # an article is a few KB; this is a ceiling, not a target
PREVIEW_CHARS = 160             # how much of the input a record keeps


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class BadRequest(Exception):
    """The request can't be served as sent. Carries the HTTP status to answer with."""

    def __init__(self, message, http_status=400):
        super().__init__(message)
        self.http_status = http_status


class Server(ThreadingHTTPServer):
    # http.server turns address reuse on. On Windows that lets a second
    # serve.py bind a port that is already taken, and the two then split the
    # requests between them. Off, the second one fails at start-up and says so.
    allow_reuse_address = False
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    server_version = "TakeMeter/1.0"
    protocol_version = "HTTP/1.1"

    # Set once in main(), shared by every request thread.
    classifier = None
    runlog = None
    model_lock = threading.Lock()

    def log_message(self, fmt, *args):
        """Silence http.server's own access lines; ours are the structured ones."""

    # ── plumbing ────────────────────────────────────────────────────────────

    def _send(self, http_status, payload):
        body = json.dumps(payload).encode("utf-8")
        try:
            self.send_response(http_status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            if http_status == 413:
                # The oversized body was never read, so the connection can't be reused.
                self.send_header("Connection", "close")
                self.close_connection = True
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionError):
            pass    # the caller hung up; nothing to send to

    def _read_json_body(self):
        """Return the request body as a dict, or raise BadRequest."""
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length) if raw_length is not None else 0
        except ValueError:
            raise BadRequest("Content-Length is not a number")
        if length <= 0:
            raise BadRequest("request body is empty; send {\"text\": \"...\"}")
        if length > MAX_BODY_BYTES:
            raise BadRequest(f"body is {length} bytes; the limit is {MAX_BODY_BYTES}", 413)

        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except UnicodeDecodeError:
            raise BadRequest("body is not valid UTF-8")
        except json.JSONDecodeError as exc:
            raise BadRequest(f"body is not valid JSON ({exc.msg} at character {exc.pos})")
        if not isinstance(payload, dict):
            raise BadRequest("body must be a JSON object like {\"text\": \"...\"}")
        return payload

    def _finish(self, record, http_status, payload, started):
        """Answer the caller. `record` is what this request did, field by field."""
        record["http_status"] = http_status
        record["duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
        if "duration_ms" in payload:
            payload["duration_ms"] = record["duration_ms"]
        self._send(http_status, payload)
        # Written after the response goes out, so duration_ms covers the send.
        self.runlog.write(record)

    def _new_record(self):
        return {
            "ts": now_iso(),
            "request_id": uuid.uuid4().hex[:12],
            "event": "request",
            "method": self.command,
            "path": self.path,
            "status": None,          # ok | rejected | error
            "http_status": None,
            "input_chars": None,
            "input_preview": None,
            "n_tokens": None,
            "n_tokens_exact": None,
            "truncated": None,
            "label": None,
            "confidence": None,
            "scores": None,
            "tokenize_ms": None,
            "model_ms": None,
            "duration_ms": None,
            "error": None,
        }

    # ── routes ──────────────────────────────────────────────────────────────

    def do_GET(self):
        started = time.perf_counter()
        record = self._new_record()
        rid = record["request_id"]

        if self.path == "/health":
            c = self.classifier
            record["status"] = "ok"
            return self._finish(record, 200, {
                "request_id": rid,
                "status": "ok",
                "labels": c.labels,
                "device": c.device,
                "max_length": c.max_length,
                "model_seed": c.meta.get("seed"),
                "trained_at": c.meta.get("trained_at"),
            }, started)

        record["status"], record["error"] = "rejected", "no such route"
        self._finish(record, 404, {
            "request_id": rid,
            "error": f"no route {self.path}; try POST /classify or GET /health",
        }, started)

    def do_POST(self):
        started = time.perf_counter()
        record = self._new_record()
        rid = record["request_id"]

        if self.path != "/classify":
            # The body is left unread, so don't try to reuse the connection.
            self.close_connection = True
            record["status"], record["error"] = "rejected", "no such route"
            return self._finish(record, 404, {
                "request_id": rid,
                "error": f"no route {self.path}; try POST /classify",
            }, started)

        try:
            payload = self._read_json_body()
            text = payload.get("text")
            if isinstance(text, str):
                record["input_chars"] = len(text)
                record["input_preview"] = text[:PREVIEW_CHARS]
            with self.model_lock:
                result = self.classifier.classify(text)

        except (BadRequest, InputError) as exc:
            record["status"], record["error"] = "rejected", str(exc)
            http_status = getattr(exc, "http_status", 400)
            return self._finish(record, http_status,
                                {"request_id": rid, "error": str(exc)}, started)

        except Exception as exc:    # the model or the tokenizer failed: our fault
            record["status"] = "error"
            record["error"] = f"{type(exc).__name__}: {exc}"
            return self._finish(record, 500, {
                "request_id": rid,
                "error": "the classifier failed on this input; it has been logged",
            }, started)

        record.update(
            status="ok",
            n_tokens=result["n_tokens"],
            n_tokens_exact=result["n_tokens_exact"],
            truncated=result["truncated"],
            label=result["label"],
            confidence=result["confidence"],
            scores=result["scores"],
            tokenize_ms=result["timings_ms"]["tokenize"],
            model_ms=result["timings_ms"]["model"],
        )
        self._finish(record, 200, {
            "request_id": rid,
            "label": result["label"],
            "confidence": result["confidence"],
            "scores": result["scores"],
            "n_tokens": result["n_tokens"],
            "n_tokens_exact": result["n_tokens_exact"],
            "truncated": result["truncated"],
            "duration_ms": None,     # filled in by _finish
        }, started)


def main():
    parser = argparse.ArgumentParser(description="Serve the TakeMeter classifier over HTTP.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--model-dir", default=str(MODEL_DIR))
    parser.add_argument("--log", default=str(LOG_PATH),
                        help="where the structured log goes (default: logs/classify.jsonl)")
    args = parser.parse_args()

    runlog = Handler.runlog = RunLog(args.log)

    def lifecycle(event, **fields):
        runlog.write({"ts": now_iso(), "event": event, "host": args.host,
                      "port": args.port, **fields})

    print("Loading the model ...", flush=True)
    load_started = time.perf_counter()
    try:
        Handler.classifier = Classifier(args.model_dir)
    except ModelNotFound as exc:
        print(f"error: {exc}", file=sys.stderr)
        lifecycle("startup", status="error", error=str(exc))
        return 1
    load_seconds = time.perf_counter() - load_started

    try:
        server = Server((args.host, args.port), Handler)
    except OSError as exc:
        message = f"could not listen on {args.host}:{args.port} ({exc})"
        print(f"error: {message}. Is another serve.py running? Try --port 8001.",
              file=sys.stderr)
        lifecycle("startup", status="error", error=message)
        return 1

    c = Handler.classifier
    lifecycle("startup", status="ok", device=c.device, labels=c.labels,
              max_length=c.max_length, model_seed=c.meta.get("seed"),
              model_trained_at=c.meta.get("trained_at"),
              model_load_ms=round(load_seconds * 1000, 1), error=None)
    print(f"Model loaded in {load_seconds:.1f}s on {c.device}: {', '.join(c.labels)}")
    print(f"Logging to {runlog.path}")
    print(f"Listening on http://{args.host}:{args.port}   (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()
        lifecycle("shutdown", status="ok", error=None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
