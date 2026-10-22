# Muther: identity, interface and sound (design only)

Status: **planned, not built.** The memory layer comes first. Nothing in this
document is implemented, and the repository is still named `jarvis` until the
rename step at the end.

## Why rename

"Jarvis" is the default name for every assistant project; it carries no identity
and collides with hundreds of repos. A name from the Alien lineage is distinctive,
and the films already define a coherent visual and sonic language for a ship
computer: monochrome text, deliberate boot sequences, low mechanical room tone,
flat synthetic speech.

Working name: **Muther** (from MU/TH/UR 6000, called "MOTHER" by the crew).
Alternatives if "Muther" proves too common: **Sulaco**, **Nostromo**, **Hadley**,
**Narcissus**. Before committing, check GitHub and the package registries: several
projects already use the "Muthur" spelling (see Prior art).

## What we take, and what we do not

Take the *grammar*: a machine that answers in clipped, factual sentences, a
terminal that shows its own state, sounds that tell you something is thinking.

Do not take assets. No film audio samples, no stills, no logos, no typefaces
ripped from the production, no imitation of the film's voice actors. The look
must be an original design in the same genre: phosphor terminal, monospace grid,
deliberate latency. The name is a reference, not a licence.

## Interface

When the assistant is running, one always-available surface shows four things:

```
MU/TH/UR 6000 · MUTHER                                    LINK  OK
──────────────────────────────────────────────────────────────────
> memory   8 notes · 1.7 KB map · last write 12:41
  voice    idle · wake "hey muther" · en-GB
  model    local · 64k ctx
──────────────────────────────────────────────────────────────────
> █
```

- **Palette:** amber `#ffb000` for primary text, dim green `#6f8f6f` for secondary
  state, near-black `#0a0a08` background; one red `#c8321e` reserved for approvals
  and failures. No rounded corners, no drop shadows.
- **Type:** a monospace face at 14-16 px, uppercase for headings and status,
  sentence case for answers. Fixed 80-column grid so lines look like printouts.
- **Boot sequence:** 1.5 s, skippable: scanlines, a short device check
  ("MEMORY ........ OK", "KNOWLEDGE ..... 8 NOTES", "VOICE ......... READY"),
  then the prompt. It runs once per app start, not per message.
- **State, not decoration:** the status rail is live data from `kb.py` (note count,
  map size, last appended finding) and from the voice layer (idle / listening /
  speaking). If memory is stale, it says so.
- **Answer rendering:** text streams in at a fixed cadence (about 30-60 chars per
  second) rather than instantly; code and paths are shown in a boxed pane, spoken
  text stays plain.
- **Approvals:** a modal strip in red, question in one line, two keys: `Y` approve,
  `N` refuse. Same content is spoken when voice is active.

Runtime options, in order of preference:

1. **Hermes desktop shell** (already Electron, already hosts voice) with a custom
   renderer skin. Least new code, keeps wake word and STT.
2. **Standalone always-on-top window** (Tauri or Electron) attached to the same
   memory layer and to the harness over HTTP.
3. **TUI theme** for the terminal path: same palette and status rail, no window.

## Sound design

All cues synthesized locally (sine/noise/tape wobble), 30-120 ms except the boot
tone. No film samples.

| cue | when | character |
|---|---|---|
| boot | app start | low 60 Hz swell, 1.2 s, then a single relay click |
| key | each accepted command | 4 ms click, quiet, no pitch |
| thinking | first token latency > 400 ms | filtered noise bed at -30 dB, fades in 200 ms |
| ready | answer complete | two short square blips, 660/880 Hz |
| alert | approval needed | repeating 3-note klaxon, max two cycles, then silence |
| error | failed action | 120 Hz saw, 90 ms, no melody |
| shutdown | app close | tape spindown, 600 ms |

Rules: nothing loops longer than 2 s; every cue is ducked under speech; the whole
set can be muted with one toggle that is itself silent.

## Voice

Target: calm, low-affect, slightly synthetic, en-GB, slower than conversational
(about 150 wpm), no audible breathing, no rising intonation on statements.

- Keep the current stack (Hermes: faster-whisper STT + Edge/Kokoro-class TTS) and
  pick the voice by **answer quality first**, latency only as a veto: anything over
  5 s to first audio is out.
- Spoken answers are a different rendering of the same text: lead sentence first,
  no paths/URLs/tables, numbers spoken plainly.
- Spoken approval gate: after "approve?", the next utterance is the answer, never
  a new request (the backtalk landmine, already documented in `docs/VOICE.md`).
- Wake word: "hey muther" (two syllables, low false-accept risk). Test in a room
  with a TV before enabling by default.

## What to borrow from the existing builds

From `krko2n/Muthur-os-terminal` (Tauri + React + Ollama):

- **Boot diagnostics as content, not animation:** the first screen lists what the
  system actually found (memory, knowledge, voice, model), then clears. Ours can
  print real counts and the map budget.
- **Status header with named fields:** platform, backend, AI model, status,
  resource cost. Translates directly to HARNESS / MODEL / CTX / MEMORY / VOICE.
- **AI panel docked to the side:** chat with an explicit stop control, suggestions
  shown for review only, warnings on destructive commands. Our approval strip is
  the same idea with fewer pixels.
- **Performance budget:** their claim is ~18 MB binary, <10% idle CPU, ~150 MB RAM.
  Ours should hold <150 MB and <5% idle with the terminal idle.
- **Installer flags:** `--dry-run`, `--no-deps`, `--prefix`. Our installers should
  support at least `-WhatIf` before they write into a harness.
- **Safe defaults with explicit overrides:** they block private-network fetches
  and broad filesystem browsing unless env flags are set. Our UI should be
  read-only by default and ask before shell actions.

From `edex-ui`: telemetry panels and a file browser are the recognisable parts;
they also age badly when the data is fake. Take live telemetry only where we have
real numbers (map size, note count, model, VRAM), and skip decorative graphs.

Skip: kiosk mode as the whole desktop (it traps the user), the 3D globe, the
built-in browser, ASCII image rendering. They are impressive and irrelevant to an
assistant that answers in text and speech.

## Prior art (checked 2026-10-22)

- `krko2n/Muthur-os-terminal` - Tauri v2 + React 19 + Ollama, cinematic terminal.
  Closest existing implementation; proves the visual language works with a local
  model. Uses the same name, so ours must diverge in behaviour, not just looks.
- `alexpritt/muthur6000` - tabletop-RPG interface, static screens.
- `loryanstrant/ha-MU-TH-UR-6000-cards` - Home Assistant cards, useful palette
  reference.
- `edex-ui` - the general "cinematic terminal" pattern (telemetry, file browser).
- Assorted CodePen recreations and an Omarchy desktop theme (LV-426): confirms the
  palette and scanline treatment are already common; differentiation comes from
  the assistant actually working, not from the skin.

## Migration checklist (when memory is stable)

1. Rename the GitHub repo; GitHub keeps redirects, so old clones keep working.
2. Rename the local directory to match (`E:\AI\<name>`).
3. Update: README, `install/persona.ps1` default paths, the OpenCode agent file's
   description, wake word in Hermes config, any `JARVIS`-named variables (none
   remain in the memory layer).
4. Rename `persona/assistant.md` header from Jarvis to the new name; keep the
   character content.
5. Only then start the interface work: palette and status rail first, boot
   sequence and sound second, streaming cadence last.

## Open questions

- Is "Muther" distinctive enough given the existing projects? Check package and
  domain availability before the rename.
- Which runtime hosts the interface: Hermes shell, or a standalone window that
  works with any harness?
- Does the interface need to work without a voice layer (text-only, headless)?
