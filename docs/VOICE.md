# Voice — pointer

The voice design and the push-to-talk tool now live in their own project:
`E:\AI\voice` (git `main`; private GitHub repo once pushed). This repo no longer
holds the design, only this pointer.

| what | where |
|---|---|
| design, decisions, landmines, build order | `E:\AI\voice\DESIGN.md` |
| how it works now: keys, spoken commands, config, how to extend | `E:\AI\voice\README.md` |
| memory note, loads only when working in that folder | `knowledge/projects/voice-input/project.md` |

Status 2026-10-27: the **input half is built and in daily use** — hold right ctrl
to record and submit, tap right shift for live dictation that types each
pause-delimited phrase into the composer, with spoken commands (`send prompt`,
`delete prompt`, `remove the last N words`, `remove the last sentence`,
`new line`). Still design: Piper spoken replies, sentence chunking, wake word,
interrupt, spoken approval.

## What stays in Muther

- `persona/assistant.md` — the spoken-first reply shape (1-3 spoken sentences,
  `---`, then the detail) is a persona rule, not tooling.
- Hermes keeps its own STT/TTS install; the install gotchas are in
  `../../assistant/voice.md` (memory repo).
- The persona and the tool are separate by decision (2026-10-27) and are expected
  to be linked later, when spoken replies need both.

## Related

- Index: `./INDEX.md`
- Persona: `../persona/assistant.md`
- Interface: `./MUTHER.md`, and `E:\AI\console`
