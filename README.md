# Muther: the assistant

The assistant layer: who it is, how it behaves, and how it speaks. It stores
nothing. Knowledge, facts and the conversation archive live in
[`victorarsenie/ai-unlimited-memory`](https://github.com/victorarsenie/ai-unlimited-memory).

```
ai-unlimited-memory                Muther
â”œâ”€â”€ knowledge/   (notes)           â”œâ”€â”€ persona/assistant.md   character + behaviour
â”œâ”€â”€ memory/      (profile, projects)â”œâ”€â”€ install/persona.ps1    writes SOUL.md / agent file
â”œâ”€â”€ kb.py                           â”œâ”€â”€ docs/VOICE.md         voice design, landmines
â”œâ”€â”€ adapters/    (harness hooks)    â””â”€â”€ skills/               (none yet)
â””â”€â”€ skills/knowledge-base
```

The split is deliberate: the assistant is the part most likely to be replaced
(Hermes today, another harness later); the memory is the part that must survive
every replacement.

## What belongs where

| thing | owner | why |
|---|---|---|
| character, tone, initiative, gates | **Muther** | it *is* the assistant; changing harness must not change it |
| voice stack, wake word, PTT, spoken mode | **Muther** | interaction, not data |
| facts, profile, projects, notes, map | **ai-unlimited-memory** | data that outlives any harness |
| conversation archive (SQLite) | **ai-unlimited-memory** | provenance, never injected wholesale |

## Install

```powershell
.\install\persona.ps1                     # Hermes SOUL.md + OpenCode agent, with backups
.\install\persona.ps1 -Only opencode      # one harness
```

The installer owns the identity slot only. The memory layer's hook is installed
separately (`ai-unlimited-memory\adapters\hermes\install.ps1`) and injects
`memory/*.md` plus `knowledge/INDEX.md` every turn.

## Skills

No skill in this repository has been written yet: the assistant's behaviour lives
in the persona, and the one skill that exists â€” `knowledge-base` â€” describes the
memory layer, so it is owned and installed by `ai-unlimited-memory`.

A skill belongs here when it describes *how Muther behaves or speaks* (voice
turn-taking, spoken confirmation, interruption handling) rather than what it
knows. `skills/` is reserved for those.

## Planned identity: Muther

The repository is still `Muther`, but the assistant is heading for a name and an
interface of its own: **Muther** (from MU/TH/UR 6000), with an amber terminal
surface, a live status rail (memory / voice / model), a short boot sequence,
synthesized cues and a calm, low-affect voice. Design only for now â€” the memory
layer ships first. Details, prior art and the rename checklist:
[`docs/MUTHER.md`](docs/MUTHER.md).

## Current state

Voice runs on Hermes because it already ships the three expensive parts: a wake
word ("Hey Hermes", off by default, `/wake`), local faster-whisper speech-to-text
with VAD, and text-to-speech. Everything that makes it Muther â€” character, memory,
knowledge â€” is outside Hermes.

`docs/VOICE.md` holds the design for a harness-independent voice loop (PTT,
sentence-level streaming, interrupt handling), the five landmines that cost real
debugging time in `backtalk`, what was taken from Muther 4.0 / Mark-LVI, and what
was rejected (Gemini Live, paid Claude plans).
