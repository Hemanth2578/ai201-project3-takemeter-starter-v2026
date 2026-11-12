#!/usr/bin/env python3
"""
Run the five capstone criteria (criteria.md, "Capstone criteria") three times.

    python capstone_eval.py --label before
    python capstone_eval.py --label after      # after the one improvement

A trial is one FRESH start of serve.py followed by the whole set of requests,
in this order:

    1. the 34 posts in test_split.csv, one at a time     criteria 1, 2 and 3
    2. one article of 900,000 characters                 criterion 3
    3. 50 requests, 10 at a time (40 good, 10 bad)       criterion 4
    4. 14 bad requests, then one good one                criterion 5

Each trial's server writes its own log, logs/eval_<label>_trial<N>.jsonl, and
the scores go to capstone_results_<label>.json. Both are evidence; commit them.

It refuses to overwrite an existing results file, so the "after" run can't
quietly replace the "before" numbers. Pass --force if you really mean to.
"""

import argparse
import csv
import json
import random
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from runlog import read_records
from send import BAD_REQUESTS

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8765
URL = f"http://{HOST}:{PORT}"
LABELS = ["Business", "Economy", "Administrative", "None of These"]

# ── The targets, copied from criteria.md ────────────────────────────────────
MIN_CORRECT = 30            # criterion 1: of 34
MIN_RECALL = 0.60           # criterion 2: every label
MAX_DURATION_MS = 100       # criterion 3: every classified request
LONG_ARTICLE_CHARS = 900_000
CONCURRENT_REQUESTS, AT_A_TIME = 50, 10     # criterion 4
BAD_ANSWER_SECONDS = 5      # criterion 5
LOG_SETTLE_SECONDS = 1.0    # serve.py writes a record just AFTER it answers


# ── talking to the server ───────────────────────────────────────────────────

def http_post(path, body, timeout=60):
    """
    POST raw bytes. Returns {"status", "json", "seconds", "problem"}.
    status is None when no HTTP answer came back at all.
    """
    started = time.perf_counter()
    out = {"status": None, "json": None, "problem": None}
    request = urllib.request.Request(
        URL + path, data=body if body is not None else b"", method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                out["status"], raw = response.status, response.read()
        except urllib.error.HTTPError as exc:
            out["status"], raw = exc.code, exc.read()
        try:
            out["json"] = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            out["problem"] = "answer was not JSON"
    except Exception as exc:                     # timeout, reset, refused
        out["problem"] = f"no answer: {type(exc).__name__}: {exc}"
    out["seconds"] = round(time.perf_counter() - started, 3)
    return out


def short_body_request(timeout):
    """
    Say Content-Length: 200, send 20 bytes, then wait for an answer.
    urllib can't lie about a length, so this one is a raw socket.
    """
    started = time.perf_counter()
    out = {"status": None, "json": None, "problem": None}
    head = (f"POST /classify HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n"
            f"Content-Type: application/json\r\nContent-Length: 200\r\n\r\n").encode()
    try:
        with socket.create_connection((HOST, PORT), timeout=timeout) as sock:
            sock.sendall(head + b'{"text": "Fed holds ')
            sock.settimeout(timeout)
            data = sock.recv(65536)
        if not data:
            out["problem"] = "no answer: connection closed with nothing sent"
        else:
            status_line, _, rest = data.partition(b"\r\n")
            out["status"] = int(status_line.split()[1])
            body = rest.partition(b"\r\n\r\n")[2]
            try:
                out["json"] = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                out["problem"] = "answer was not JSON"
    except Exception as exc:
        out["problem"] = f"no answer: {type(exc).__name__}: {exc}"
    out["seconds"] = round(time.perf_counter() - started, 3)
    return out


def classify_body(text):
    return json.dumps({"text": text}).encode("utf-8")


def start_server(log_path):
    """A fresh serve.py on its own log. Returns the process once it is listening."""
    if log_path.exists():
        log_path.unlink()
    proc = subprocess.Popen(
        [sys.executable, "serve.py", "--port", str(PORT), "--log", str(log_path)],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 120
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("serve.py exited at start-up:\n"
                               + proc.stdout.read().decode("utf-8", "replace"))
        try:
            # Connect and hang up. That proves it is listening without sending
            # a request, so the first REQUEST the server sees is criterion 3's.
            socket.create_connection((HOST, PORT), timeout=1).close()
            return proc
        except OSError:
            time.sleep(0.5)
    proc.kill()
    raise RuntimeError("serve.py did not start listening within 120 s")


def stop_server(proc):
    proc.terminate()
    try:
        output, _ = proc.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()
        output, _ = proc.communicate()
    return output.decode("utf-8", "replace")


def held_out():
    with open(ROOT / "test_split.csv", encoding="utf-8", newline="") as f:
        return [(r["text"], r["label"]) for r in csv.DictReader(f)]


def records_by_id(log_path):
    records, _ = read_records(log_path)
    by_id = {}
    for r in records:
        if r.get("event") == "request":
            by_id.setdefault(r.get("request_id"), []).append(r)
    return by_id


# ── the four stages of a trial ──────────────────────────────────────────────

def stage_held_out(posts):
    """Send the 34 posts one at a time. First thing the fresh server sees."""
    rows = []
    for text, truth in posts:
        answer = http_post("/classify", classify_body(text))
        body = answer["json"] if isinstance(answer["json"], dict) else {}
        rows.append({
            "truth": truth,
            "status": answer["status"],
            "label": body.get("label"),
            "confidence": body.get("confidence"),
            "request_id": body.get("request_id"),
            "problem": answer["problem"],
            "preview": " ".join(text.split())[:70],
        })
    return rows


def stage_long_article():
    sentence = "The city council approved a new water budget for the coming year. "
    text = (sentence * (LONG_ARTICLE_CHARS // len(sentence) + 1))[:LONG_ARTICLE_CHARS]
    answer = http_post("/classify", classify_body(text), timeout=300)
    body = answer["json"] if isinstance(answer["json"], dict) else {}
    return {
        "chars": len(text),
        "status": answer["status"],
        "label": body.get("label"),
        "n_tokens": body.get("n_tokens"),
        "request_id": body.get("request_id"),
        "client_seconds": answer["seconds"],
        "problem": answer["problem"],
    }


def stage_concurrent(posts, trial):
    """40 good and 10 bad, shuffled, 10 in flight at a time."""
    good = [("good", "/classify", classify_body(text)) for text, _ in (posts + posts)[:40]]
    bad = [(name, path, body) for name, body, path in BAD_REQUESTS[:10]]
    jobs = good + bad
    random.Random(trial).shuffle(jobs)

    def run(job):
        name, path, body = job
        answer = http_post(path, body)
        got = answer["json"] if isinstance(answer["json"], dict) else {}
        return {"kind": name, "status": answer["status"], "label": got.get("label"),
                "request_id": got.get("request_id"), "problem": answer["problem"]}

    with ThreadPoolExecutor(max_workers=AT_A_TIME) as pool:
        return list(pool.map(run, jobs))


def stage_bad_requests(posts):
    """14 requests that should each be refused inside 5 seconds, then a good one."""
    cases = [(name, "post", path, body) for name, body, path in BAD_REQUESTS]
    cases.append(("not valid UTF-8", "post", "/classify", b'{"text": "\xff\xfe\xfa"}'))
    cases.append(("body shorter than Content-Length", "short", "/classify", None))
    cases.append(("JSON nested 100,000 deep", "post", "/classify",
                  b'{"text": ' + b"[" * 100_000 + b"]" * 100_000 + b"}"))

    rows = []
    for name, how, path, body in cases:
        if how == "short":
            answer = short_body_request(BAD_ANSWER_SECONDS)
        else:
            answer = http_post(path, body, timeout=BAD_ANSWER_SECONDS)
        got = answer["json"]
        refused = (
            answer["status"] is not None and 400 <= answer["status"] < 500
            and isinstance(got, dict) and "error" in got
            and answer["seconds"] <= BAD_ANSWER_SECONDS
        )
        rows.append({
            "case": name,
            "status": answer["status"],
            "error": got.get("error") if isinstance(got, dict) else None,
            "seconds": answer["seconds"],
            "problem": answer["problem"],
            "refused": refused,
        })

    follow_up = http_post("/classify", classify_body(posts[0][0]))
    return rows, follow_up["status"]


# ── scoring ─────────────────────────────────────────────────────────────────

def score_trial(trial, label, posts):
    log_path = ROOT / "logs" / f"eval_{label}_trial{trial}.jsonl"
    proc = start_server(log_path)
    try:
        rows = stage_held_out(posts)
        long_article = stage_long_article()
        concurrent = stage_concurrent(posts, trial)
        bad_rows, follow_up_status = stage_bad_requests(posts)
        time.sleep(LOG_SETTLE_SECONDS)
    finally:
        server_output = stop_server(proc)
    by_id = records_by_id(log_path)
    criteria = {}

    # 1. accuracy through the endpoint
    correct = sum(r["label"] == r["truth"] for r in rows)
    criteria["1"] = {
        "score": f"{correct}/{len(rows)}", "met": correct >= MIN_CORRECT,
        "wrong": [{"truth": r["truth"], "got": r["label"], "confidence": r["confidence"],
                   "preview": r["preview"]} for r in rows if r["label"] != r["truth"]],
    }

    # 2. every label's recall
    recall = {}
    for name in LABELS:
        mine = [r for r in rows if r["truth"] == name]
        recall[name] = round(sum(r["label"] == name for r in mine) / len(mine), 3) if mine else None
    lowest = min((v, k) for k, v in recall.items() if v is not None)
    criteria["2"] = {
        "score": f"{lowest[0]:.2f} lowest ({lowest[1]})", "met": lowest[0] >= MIN_RECALL,
        "recall": recall,
    }

    # 3. no classified request over 100 ms: the 34, then the long article
    timed = []
    for position, r in enumerate(rows + [long_article], 1):
        record = (by_id.get(r["request_id"]) or [None])[0]
        timed.append({
            "position": position,
            "what": "900,000-character article" if position == len(rows) + 1 else "held-out post",
            "status": r["status"],
            "duration_ms": record.get("duration_ms") if record else None,
            "tokenize_ms": record.get("tokenize_ms") if record else None,
            "model_ms": record.get("model_ms") if record else None,
            "n_tokens": record.get("n_tokens") if record else None,
        })
    within = [t for t in timed if t["status"] == 200 and t["duration_ms"] is not None
              and t["duration_ms"] <= MAX_DURATION_MS]
    durations = [t["duration_ms"] for t in timed if t["duration_ms"] is not None]
    criteria["3"] = {
        "score": f"{len(within)}/{len(timed)}", "met": len(within) == len(timed),
        "over": [t for t in timed if t not in within],
        "slowest_ms": max(durations) if durations else None,
        "median_ms": sorted(durations)[len(durations) // 2] if durations else None,
    }

    # 4. the log agrees with what was sent, 10 at a time
    agree, disagreements = 0, []
    for c in concurrent:
        found = by_id.get(c["request_id"], []) if c["request_id"] else []
        ok = (c["status"] is not None and len(found) == 1
              and found[0].get("http_status") == c["status"]
              and found[0].get("label") == c["label"])
        agree += ok
        if not ok:
            disagreements.append({**c, "records_found": len(found)})
    criteria["4"] = {
        "score": f"{agree}/{len(concurrent)}", "met": agree == len(concurrent),
        "disagreements": disagreements,
        "statuses_sent": {str(s): sum(1 for c in concurrent if c["status"] == s)
                          for s in sorted({c["status"] for c in concurrent}, key=str)},
    }

    # 5. bad requests refused within 5 s, and the server still works after
    refused = sum(r["refused"] for r in bad_rows)
    criteria["5"] = {
        "score": f"{refused}/{len(bad_rows)}, then {follow_up_status}",
        "met": refused == len(bad_rows) and follow_up_status == 200,
        "not_refused": [r for r in bad_rows if not r["refused"]],
        "cases": bad_rows,
        "follow_up_status": follow_up_status,
    }

    return {
        "trial": trial,
        "log": str(log_path.relative_to(ROOT)).replace("\\", "/"),
        "log_records": sum(len(v) for v in by_id.values()),
        "criteria": criteria,
        "server_output_tail": server_output[-3000:],
    }


TITLES = {
    "1": ("Endpoint as accurate as the notebook", "30 of 34"),
    "2": ("Every label's recall through the endpoint", "≥ 0.60"),
    "3": ("No classified request over 100 ms", "35 of 35"),
    "4": ("Log agrees with what was sent, 10 at a time", "50 of 50"),
    "5": ("Bad request refused within 5 s, server still up", "14 of 14, then 200"),
}


def run_log_table(trials):
    lines = ["| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |",
             "|---|---|---|---|---|---|"]
    for key, (title, target) in TITLES.items():
        cells = [t["criteria"][key]["score"] for t in trials]
        verdict = "MET" if all(t["criteria"][key]["met"] for t in trials) else "MISSED"
        lines.append(f"| {key}. {title} | {target} | {' | '.join(cells)} | {verdict} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run the five capstone criteria, three trials.")
    parser.add_argument("--label", required=True, help="before or after")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing results file for this label")
    args = parser.parse_args()

    out_file = ROOT / f"capstone_results_{args.label}.json"
    if out_file.exists() and not args.force:
        print(f"{out_file.name} already exists. Use a different --label, or --force.")
        return 1

    posts = held_out()
    trials = []
    for trial in range(1, args.trials + 1):
        print(f"\n=== trial {trial} of {args.trials}: fresh serve.py ===", flush=True)
        result = score_trial(trial, args.label, posts)
        trials.append(result)
        for key, (title, _) in TITLES.items():
            c = result["criteria"][key]
            print(f"  {key}. {title:<48} {c['score']:<28} {'met' if c['met'] else 'MISSED'}")

    out_file.write_text(json.dumps({
        "label": args.label,
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "n_trials": args.trials,
        "trials": trials,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{run_log_table(trials)}\n")
    print(f"Wrote {out_file.name} and logs/eval_{args.label}_trial*.jsonl. Commit them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
