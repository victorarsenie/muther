# Jarvis: the assistant layer

The voice assistant, kept deliberately thin and portable. It does not store
anything: memory, knowledge and the conversation archive live in
[`victorarsenie/ai-unlimited-memory`](https://github.com/victorarsenie/ai-unlimited-memory).

This split is the point. The assistant is the part most likely to be replaced
(Hermes today, another harness tomorrow); the memory is the part that must
survive every replacement.

```
ai-unlimited-memory          jarvis
├── knowledge/  (notes)      ├── docs/VOICE.md     voice design, landmines
├── memory/     (persona)    ├── adapters?         no: they belong to memory
├── kb.py                    └── (voice code later)
└── adapters/ (harness hooks)
```

## The contract

1. The memory layer injects `memory/*.md` and `knowledge/INDEX.md` into every turn
   through a harness hook (`MEMORY_HOME`, default
   `E:\AI\memory\PersonalMemory`).
2. The assistant adds voice and nothing else: speech in, speech out, spoken
   permission gates. It reads the same injected context as any other client.
3. Persona lives in the memory layer (`memory/persona.md`) so a harness change
   does not change the assistant's character.

## Current state

Voice runs on Hermes because it already ships the three expensive parts: a wake
word ("Hey Hermes", off by default, `/wake`), local faster-whisper speech-to-text
with VAD, and text-to-speech. Everything that makes it ours — persona, memory,
knowledge — is outside Hermes.

`docs/VOICE.md` records the design for a harness-independent voice loop (PTT,
sentence-level streaming, interrupt handling) and the five landmines that cost
real debugging time in `backtalk`, plus what was taken from JARVIS 4.0 /
Mark-LVI and what was rejected (Gemini Live, paid Claude plans).

## Status

- Memory layer: built and in daily use (`ai-unlimited-memory`).
- Voice: on Hermes, native; no custom audio code in this repo yet.
- OpenCode: can host the same assistant later via the v2 HTTP API
  (`prompt_async`, `/event`, `abort`, permission routing) — documented in
  `docs/VOICE.md`.
