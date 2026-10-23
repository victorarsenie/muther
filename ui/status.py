#!/usr/bin/env python3
"""Collect machine state for the Muther interface.

Writes one JSON document. Everything here is measured, nothing is estimated:
GPU through nvidia-smi, RAM through GlobalMemoryStatusEx, ports through a TCP
connect, the memory layer by reading its files, activity from the injection log.

    python status.py            # write status.json next to this file
    python status.py --json     # print it instead

Stdlib only. Takes ~150 ms because tasklist and nvidia-smi are subprocesses.
"""
from __future__ import annotations

import ctypes
import json
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(r"E:\AI\memory\ai-unlimited-memory")
OUT = Path(__file__).resolve().parent / "status.json"
INJECT_LOG = Path(__import__("os").environ.get("TEMP", r"C:\Windows\Temp")) / "kb-inject.log"
PORTS = {8080: "model server", 8090: "embedder", 3000: "portfolio dev"}


def _run(cmd: list[str], timeout: float = 4.0) -> str:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip()
    except Exception:
        return ""


def gpu() -> dict:
    out = _run(["nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,power.draw",
                "--format=csv,noheader,nounits"])
    if not out:
        return {"present": False}
    name, total, used, free, util, power = [p.strip() for p in out.split(",")]
    return {
        "present": True, "name": name,
        "total_mib": int(float(total)), "used_mib": int(float(used)),
        "free_mib": int(float(free)), "util_pct": int(float(util)),
        "power_w": float(power) if power not in ("[N/A]", "") else None,
    }


def ram() -> dict:
    class MEMSTATUS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

    stat = MEMSTATUS()
    stat.dwLength = ctypes.sizeof(MEMSTATUS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    return {
        "total_mib": int(stat.ullTotalPhys / 1048576),
        "available_mib": int(stat.ullAvailPhys / 1048576),
        "load_pct": int(stat.dwMemoryLoad),
    }


def disk(letter: str = "E:") -> dict:
    try:
        free = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(letter + "\\"), None, None, ctypes.byref(free))
        return {"drive": letter, "free_gib": round(free.value / 1073741824, 1)}
    except Exception:
        return {"drive": letter, "free_gib": None}


def ports() -> list[dict]:
    out = []
    for port, what in PORTS.items():
        s = socket.socket()
        s.settimeout(0.15)
        try:
            s.connect(("127.0.0.1", port))
            out.append({"port": port, "what": what, "open": True})
        except OSError:
            out.append({"port": port, "what": what, "open": False})
        finally:
            s.close()
    return out


def processes() -> list[dict]:
    """Engine processes only: the ones that hold the card."""
    wanted = {"llama-server.exe", "strata.exe", "strata-poly.exe"}
    out = []
    for line in _run(["tasklist", "/fo", "csv", "/nh"]).splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) < 2 or parts[0].lower() not in wanted:
            continue
        rss_mib = 0
        digits = "".join(c for c in parts[-1].split()[0] if c.isdigit())
        if digits:
            rss_mib = round(int(digits) / 1024)
        out.append({"name": parts[0], "pid": int(parts[1]) if parts[1].isdigit() else None,
                    "rss_mib": rss_mib})
    return out


def _tail_lines(path: Path, count: int = 5) -> list[str]:
    try:
        with path.open("rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - 8192))
            lines = fh.read().decode("utf-8", "replace").splitlines()
        return [ln for ln in lines if ln.strip()][-count:]
    except OSError:
        return []


def memory_layer() -> dict:
    kb = HOME / "knowledge"
    notes = [p for p in kb.rglob("*.md")
             if p.name.lower() not in ("index.md", "_domain.md")
             and "_archive" not in p.parts and "pending" not in p.parts]
    try:
        map_size = (kb / "INDEX.md").stat().st_size
    except OSError:
        map_size = 0
    tail = _tail_lines(INJECT_LOG, 1)
    last = tail[-1] if tail else ""
    return {
        "notes": len(notes),
        "map_chars": map_size,
        "last_injection": last[:120] if last else None,
        "log_lines": _tail_lines(INJECT_LOG, 5),
    }


def collect() -> dict:
    g, r = gpu(), ram()
    alerts = []
    if g.get("present") and g["free_mib"] < 1024:
        alerts.append(f"VRAM free {g['free_mib']} MiB - below the 1024 reserve")
    if g.get("present") and g["free_mib"] < 300:
        alerts.append("VRAM in the WDDM eviction zone (<300 MiB)")
    if r["available_mib"] < 2048:
        alerts.append(f"RAM available {r['available_mib']} MiB - expert spill likely")
    if any(p["port"] == 8080 and not p["open"] for p in ports()):
        pass  # no alert: the model being down is a normal state
    return {
        "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "gpu": g, "ram": r, "disk": disk(), "ports": ports(),
        "processes": processes(), "memory": memory_layer(), "alerts": alerts,
    }


def main() -> int:
    data = collect()
    if "--json" in sys.argv:
        print(json.dumps(data, indent=2))
        return 0
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"status: {OUT} ({len(data['alerts'])} alert(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
