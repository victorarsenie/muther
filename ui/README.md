# Muther interface

Two surfaces over the same collector, plus engine control.

```
muther.bat                 # the terminal board (default)
python tui.py              # same, without the .bat
python window.py --open    # the same board as a Chrome app window
python status.py --json    # the raw document
```

## Keys (terminal board)

| key | action |
|---|---|
| `1` `2` `3` | start that engine, or arm a stop for it (press again within 4 s) |
| `s` | stop every engine this board started |
| `w` | open the window server on :8123 and launch Chrome at it |
| `r` | refresh now |
| `q` | quit |

Engines: `1` swift 120k, `2` coder strata, `3` swift 64k agent. The registry and
the guards live in `actions.py` — edit there to change what the keys mean.

## Guards (the point of `actions.py`)

- Refuses to start while **:8080 is occupied** — one arm at a time, or the next
  process silently talks to a stale model.
- Refuses to start a second engine while one it started is alive.
- Stops only processes it started (pid recorded in `engines.json`), with
  `taskkill /T`, because the launcher is a `.bat` that spawns the server.
- `s` and the second press on a key are the only ways to stop: nothing stops a
  model because a window closed.

## Measured cost

| surface | RAM | VRAM |
|---|---|---|
| terminal board | 17 MB | 0 |
| Chrome app window | 529 MB | ~3 MB |

The board is the default because at 150k the coder leaves ~1–2 GiB free, and expert
spill costs measured disk reads (342 GB at 200k, 11 GB at 150k). Open the window
when no model is loaded; close it before a benchmark.

## What is verified

- Collector reads GPU, RAM, disk, ports, engine processes, knowledge counts and
  the last injection line; `--json` and `--once` both render.
- Port guard: with a dummy listener on :8080, `--start 1` refuses and exits 1.
- Window server: `GET /` returns 200 with live values; `<meta refresh>` drives it.
- Boot chime uses `winsound.Beep` (synthesised, no sample files).

## What is not verified

No engine has been started by this board yet: that is a model run, and model runs
are explicit work. Pressing `1` is the test, when you want it.
