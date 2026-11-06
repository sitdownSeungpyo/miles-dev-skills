#!/usr/bin/env python3
"""Orchestration monitor — local web GUI showing which models/agents are working
and their token usage, read from Claude Code transcripts (~/.claude/projects).

Stdlib only. Binds to 127.0.0.1. Read-only: never writes to ~/.claude.

  python3 monitor.py [--port 8765] [--hours 24] [--open] [--claude-dir ~/.claude]
"""
import argparse
import json
import os
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ACTIVE_SECS = 90  # transcript written within this window => "active"
_cache = {}  # path -> (mtime, size, summary)
_lock = threading.Lock()


def _blank_usage():
    return {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "messages": 0}


def _add_usage(dst, u):
    dst["input"] += u.get("input_tokens") or 0
    dst["output"] += u.get("output_tokens") or 0
    dst["cache_read"] += u.get("cache_read_input_tokens") or 0
    dst["cache_write"] += u.get("cache_creation_input_tokens") or 0
    dst["messages"] += 1


def _tool_label(block):
    inp = block.get("input") or {}
    for key in ("description", "command", "file_path", "pattern", "query", "url", "prompt"):
        v = inp.get(key)
        if isinstance(v, str) and v.strip():
            v = v.strip().splitlines()[0]
            return f"{block.get('name')}: {v[:90]}"
    return block.get("name") or "tool"


def parse_transcript(path):
    """Summarize one .jsonl transcript. Cached by (mtime, size)."""
    try:
        st = path.stat()
    except OSError:
        return None
    with _lock:
        hit = _cache.get(str(path))
        if hit and hit[0] == st.st_mtime and hit[1] == st.st_size:
            return hit[2]
    by_model, seen = {}, set()
    title = last_prompt = cwd = None
    first_ts = last_ts = None
    last_action = None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                t = rec.get("type")
                ts = rec.get("timestamp")
                if ts:
                    first_ts = first_ts or ts
                    last_ts = ts
                if t == "ai-title":
                    title = rec.get("aiTitle") or title
                elif t == "agent-name" and not title:
                    title = rec.get("agentName")
                elif t == "last-prompt":
                    last_prompt = rec.get("lastPrompt")
                elif t == "assistant":
                    cwd = rec.get("cwd") or cwd
                    msg = rec.get("message") or {}
                    content = msg.get("content") or []
                    if isinstance(content, list):
                        for b in content:
                            if isinstance(b, dict) and b.get("type") == "tool_use":
                                last_action = _tool_label(b)
                    mid = msg.get("id") or rec.get("requestId")
                    model = msg.get("model")
                    usage = msg.get("usage")
                    if not mid or mid in seen or not usage or not model or model.startswith("<"):
                        continue
                    seen.add(mid)
                    _add_usage(by_model.setdefault(model, _blank_usage()), usage)
    except OSError:
        return None
    summary = {
        "by_model": by_model,
        "title": title,
        "last_prompt": last_prompt,
        "cwd": cwd,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "last_action": last_action,
        "mtime": st.st_mtime,
    }
    with _lock:
        _cache[str(path)] = (st.st_mtime, st.st_size, summary)
    return summary


def _sum(models):
    tot = _blank_usage()
    for u in models.values():
        for k in tot:
            tot[k] += u[k]
    return tot


def collect(claude_dir, hours):
    now = time.time()
    cutoff = now - hours * 3600
    projects = Path(claude_dir).expanduser() / "projects"
    sessions, totals = [], {}
    if not projects.is_dir():
        return {"error": f"not found: {projects}", "sessions": [], "totals": {}}
    for proj in projects.iterdir():
        if not proj.is_dir():
            continue
        for tf in proj.glob("*.jsonl"):
            try:
                if tf.stat().st_mtime < cutoff:
                    continue
            except OSError:
                continue
            main = parse_transcript(tf)
            if not main:
                continue
            subs = []
            subdir = proj / tf.stem / "subagents"
            if subdir.is_dir():
                for af in subdir.glob("agent-*.jsonl"):
                    s = parse_transcript(af)
                    if not s:
                        continue
                    meta = {}
                    mf = af.with_name(af.stem + ".meta.json")
                    try:
                        meta = json.loads(mf.read_text())
                    except (OSError, ValueError):
                        pass
                    finished = meta.get("finished")
                    recent = (now - s["mtime"]) < ACTIVE_SECS
                    if finished is True:
                        status = "done"
                    elif finished is False:
                        status = "running" if recent else "waiting"  # e.g. long tool call
                    else:
                        status = "running" if recent else "done"
                    subs.append({
                        "id": af.stem.replace("agent-", ""),
                        "type": meta.get("agentType") or "agent",
                        "description": meta.get("description") or s.get("title"),
                        "status": status,
                        "by_model": s["by_model"],
                        "total": _sum(s["by_model"]),
                        "last_action": s["last_action"],
                        "first_ts": s["first_ts"],
                        "last_ts": s["last_ts"],
                    })
                    for m, u in s["by_model"].items():
                        _add_into(totals, m, u)
            subs.sort(key=lambda x: x["last_ts"] or "", reverse=True)
            for m, u in main["by_model"].items():
                _add_into(totals, m, u)
            all_models = {}
            for src in [main["by_model"]] + [x["by_model"] for x in subs]:
                for m, u in src.items():
                    _add_into(all_models, m, u)
            sessions.append({
                "id": tf.stem,
                "project": proj.name,
                "cwd": main["cwd"],
                "title": main["title"] or (main["last_prompt"] or "")[:60] or tf.stem[:8],
                "last_prompt": main["last_prompt"],
                "active": (now - main["mtime"]) < ACTIVE_SECS,
                "last_ts": main["last_ts"],
                "last_action": main["last_action"],
                "main_by_model": main["by_model"],
                "main_total": _sum(main["by_model"]),
                "all_by_model": all_models,
                "all_total": _sum(all_models),
                "subagents": subs,
            })
    sessions.sort(key=lambda x: x["last_ts"] or "", reverse=True)
    return {"generated": now, "hours": hours, "sessions": sessions, "totals": totals}


def _add_into(dst, model, u):
    d = dst.setdefault(model, _blank_usage())
    for k in d:
        d[k] += u[k]


HTML = (Path(__file__).with_name("monitor.html"))


class Handler(BaseHTTPRequestHandler):
    claude_dir = "~/.claude"
    hours = 24

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/data":
            q = parse_qs(url.query)
            try:
                hours = float(q.get("hours", [self.hours])[0])
            except ValueError:
                hours = self.hours
            hours = max(0.1, min(hours, 24 * 90))
            self._send(200, json.dumps(collect(self.claude_dir, hours)), "application/json")
        elif url.path in ("/", "/index.html"):
            try:
                self._send(200, HTML.read_bytes(), "text/html; charset=utf-8")
            except OSError as e:
                self._send(500, f"monitor.html missing: {e}", "text/plain")
        else:
            self._send(404, "not found", "text/plain")


def _alive(url):
    import urllib.request
    try:
        with urllib.request.urlopen(url + "api/data?hours=0.1", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def launch(args):
    import shutil
    import subprocess
    import tempfile
    url = f"http://127.0.0.1:{args.port}/"
    if _alive(url):
        print(f"already running: {url}")
    else:
        log = Path(tempfile.gettempdir()) / f"orchestration-monitor-{args.port}.log"
        cmd = [sys.executable, "-I", str(Path(__file__).resolve()), "--port", str(args.port),
               "--hours", str(args.hours), "--claude-dir", args.claude_dir]
        kw = {"stdout": open(log, "a"), "stderr": subprocess.STDOUT, "stdin": subprocess.DEVNULL}
        if os.name == "nt":
            kw["creationflags"] = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        else:
            kw["start_new_session"] = True
        proc = subprocess.Popen(cmd, **kw)
        for _ in range(30):
            if _alive(url):
                break
            time.sleep(0.2)
        else:
            print(f"server did not come up; see {log}", file=sys.stderr)
            sys.exit(1)
        print(f"started pid {proc.pid}: {url}  (log: {log})")
    cmux = shutil.which("cmux")
    if cmux and os.environ.get("CMUX_WORKSPACE_ID"):
        r = subprocess.run([cmux, "browser", "open-split", url, "--focus", "true"], capture_output=True, text=True)
        if r.returncode == 0:
            print("opened in cmux browser split")
            return
        print(f"cmux open-split failed ({r.stderr.strip() or r.returncode}); falling back to default browser")
    webbrowser.open(url)
    print("opened in default browser")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--hours", type=float, default=24, help="default time window")
    ap.add_argument("--claude-dir", default=os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
    ap.add_argument("--open", action="store_true", help="open the dashboard in the default browser")
    ap.add_argument("--dump", action="store_true", help="print JSON once and exit (no server)")
    ap.add_argument("--launch", action="store_true",
                    help="start the server detached if not running, open it (cmux split inside cmux, else browser), exit")
    args = ap.parse_args()

    if args.launch:
        launch(args)
        return
    if args.dump:
        print(json.dumps(collect(args.claude_dir, args.hours), indent=2, ensure_ascii=False))
        return
    Handler.claude_dir, Handler.hours = args.claude_dir, args.hours
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as e:
        print(f"port {args.port} unavailable ({e}). Already running? Try --port {args.port + 1}", file=sys.stderr)
        sys.exit(1)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"orchestration monitor: {url}  (Ctrl+C to stop)", flush=True)
    if args.open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
