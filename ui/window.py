#!/usr/bin/env python3
"""Muther's window: a real app window over the live machine state.

    python window.py                 # serve on :8123, open nothing
    python window.py --open          # serve and open a Chrome app window
    python window.py --open --disable-gpu

The page is plain HTML/CSS/JS in `web/` served by a stdlib HTTP server; the window
is Chrome in app mode (no tabs, no address bar), which is why it reads as a native
app without shipping Electron or building Tauri.

Routes:
    GET  /                    the dashboard
    GET  /app.css /app.js     static assets
    GET  /api/state           collector JSON
    POST /api/engine?key=1&action=start|stop    engine control with guards

Measured cost: ~529 MB RAM, ~3 MB VRAM while open. Close it before a benchmark;
at 150k the coder leaves only ~1-2 GiB free.
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import actions
import status as collector

PORT = 8123
WEB = Path(__file__).resolve().parent / "web"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".js": "application/javascript; charset=utf-8", ".svg": "image/svg+xml"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: dict, code: int = 200) -> None:
        self._send(code, json.dumps(payload).encode("utf-8"), "application/json")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/state":
            try:
                self._json(collector.collect())
            except Exception as exc:
                self._json({"error": str(exc)}, 500)
            return
        file = WEB / ("index.html" if path == "/" else path.lstrip("/"))
        if not file.is_file() or WEB not in file.resolve().parents:
            self._send(404, b"not found", "text/plain")
            return
        self._send(200, file.read_bytes(), TYPES.get(file.suffix, "application/octet-stream"))

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/engine":
            self._json({"ok": False, "message": "unknown endpoint"}, 404)
            return
        query = parse_qs(parsed.query)
        key = (query.get("key") or [""])[0]
        action = (query.get("action") or [""])[0]
        try:
            if action == "start":
                ok, message = actions.start(key)
            elif action == "stop":
                ok, message = actions.stop(key)
            else:
                ok, message = False, f"unknown action: {action}"
        except Exception as exc:
            ok, message = False, f"{key}: {exc}"
        self._json({"ok": ok, "message": message})

    def log_message(self, *args) -> None:
        pass


def serve(port: int = PORT) -> ThreadingHTTPServer:
    """Bind the dashboard server; the caller decides where it runs."""
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> int:
    global PORT
    args = sys.argv[1:]
    if "--port" in args:
        PORT = int(args[args.index("--port") + 1])
    httpd = serve(PORT)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"window: {url}")
    if "--open" in args:
        if not CHROME.is_file():
            print("window: chrome not found, open the URL manually")
        else:
            flags = [str(CHROME), f"--app={url}", "--window-size=1220,840",
                     "--no-first-run", "--no-default-browser-check",
                     f"--user-data-dir={Path.home() / '.muther-ui'}"]
            if "--disable-gpu" in args:
                flags.append("--disable-gpu")
            threading.Timer(0.8, lambda: subprocess.Popen(
                flags, creationflags=0x00000008,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
