#!/usr/bin/env python3
"""The same board as a window, for when the card is idle.

    python window.py                 # serve on :8123, do not open anything
    python window.py --open          # serve and open a Chrome app window
    python window.py --open --disable-gpu   # same, no GPU compositing

Cost measured on this box: ~529 MB RAM as a Chrome app window, ~3 MB VRAM for a
static page. That is why it is a toggle and not the default face: at 150k the
coder leaves only ~1-2 GiB free, and expert spill costs measured disk reads.

Slot the launcher as:  ui\\window.bat --open
Stdlib only; renders the same collector data, no framework, no build step.
"""
from __future__ import annotations

import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import status as collector

PORT = 8123
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

PAGE = """<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="3">
<title>MU/TH/UR 6000</title>
<style>
  html,body {{ margin:0; background:#0b0b0c; color:#ffb000;
    font-family: Consolas, "Cascadia Mono", monospace; }}
  .frame {{ padding:22px 26px; max-width:980px; }}
  h1 {{ font-size:15px; letter-spacing:.28em; font-weight:600; margin:0 0 14px;
    color:#ffd27a; }}
  h1 span {{ float:right; color:#8a6a2a; letter-spacing:.1em; }}
  section {{ border:1px solid #4a3512; margin:10px 0; padding:8px 12px; }}
  h2 {{ font-size:11px; letter-spacing:.22em; color:#8a6a2a; margin:0 0 6px;
    font-weight:500; text-transform:uppercase; }}
  .row {{ font-size:13px; line-height:1.55; white-space:pre; }}
  .dim {{ color:#8a6a2a; }}
  .ok {{ color:#8fd18f; }}
  .bad {{ color:#ff6b5e; }}
  .bar {{ color:#ffb000; }}
</style></head><body><div class="frame">
<h1>MU/TH/UR 6000 <span>{clock}</span></h1>
{sections}
</div></body></html>"""


def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def section(title: str, rows: list[str]) -> str:
    body = "".join(f'<div class="row">{r}</div>' for r in rows)
    return f"<section><h2>{esc(title)}</h2>{body}</section>"


def page(data: dict) -> bytes:
    g, r, m = data["gpu"], data["ram"], data["memory"]
    out = []
    if g.get("present"):
        out.append(section("power / vram", [
            f"{esc(g['name'])}   {g['used_mib']} / {g['total_mib']} MiB",
            f'<span class="bar">free {g["free_mib"]} MiB   util {g["util_pct"]}%   '
            f'power {g["power_w"]} W</span>',
        ]))
    out.append(section("memory", [
        f"{r['available_mib']} MiB available of {r['total_mib']}   load {r['load_pct']}%",
        f'<span class="dim">{data["disk"]["drive"]} free {data["disk"]["free_gib"]} GiB</span>',
    ]))
    out.append(section("engines", [
        "".join(f'<span class="{"ok" if p["open"] else "dim"}">:{p["port"]} {esc(p["what"])}</span>'
                + ("&nbsp;&nbsp;" if p["open"] else "&nbsp;&nbsp;") for p in data["ports"]),
        *[f'<span class="dim">pid {p["pid"]}   {esc(p["name"])}   rss {p["rss_mib"]} MiB</span>'
          for p in data["processes"]],
    ]))
    out.append(section("knowledge", [
        f"{m['notes']} notes   map {m['map_chars']} chars",
        f'<span class="dim">{esc((m["last_injection"] or "")[:110])}</span>',
    ]))
    alert_rows = [f'<span class="bad">{esc(a)}</span>' for a in data["alerts"]] or \
                 ['<span class="ok">all systems within limits</span>']
    out.append(section("attention", alert_rows))
    return PAGE.format(clock=time.strftime("%H:%M:%S"), sections="".join(out)).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        try:
            body = page(collector.collect())
        except Exception as exc:  # never kill the server for one bad read
            body = f"collector error: {exc}".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:
        pass


def main() -> int:
    args = sys.argv[1:]
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"window: http://127.0.0.1:{PORT}/")
    if "--open" in args:
        if not CHROME.is_file():
            print("window: chrome not found, open the URL manually")
        else:
            flags = [str(CHROME), f"--app=http://127.0.0.1:{PORT}/",
                     "--window-size=1000,760", "--no-first-run",
                     f"--user-data-dir={Path.home() / '.muther-ui'}"]
            if "--disable-gpu" in args:
                flags.append("--disable-gpu")
            threading.Timer(0.8, lambda: subprocess.Popen(flags)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
