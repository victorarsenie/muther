# Jarvis: one memory layer for every harness

A local-first assistant memory that does not belong to any single agent. Notes are
plain markdown; a generated map is injected into every turn; each harness gets a
thin adapter instead of a private database.

Built for a Windows workstation running local models, but nothing in the design
depends on Windows, a specific model, or a hosted API.

## Why

Every agent harness ships its own memory: OpenCode has an embedding store, Hermes
has capped notes plus an index hook, Claude Code has none. The same fact ends up
stored three times and none of the copies is canonical. This repo is the missing
layer: **one corpus, one map, many readers**.

## How it works

```
knowledge/            notes, one per topic (canonical, human-editable)
  INDEX.md            generated map, <= 3000 chars, injected every turn
memory/               small always-on memory: persona, profile, projects
jobs/                 per-task reading lists (priming)
adapters/
  hermes/             pre_llm_call hook (stdin JSON -> {"context": ...})
  opencode/           plugin on the chat.message hook
kb.py                 index / lint / search / show / append / rmfact
```

Two layers, deliberately different:

| layer | size | injected | changes |
|---|---|---|---|
| memory | kilobytes | every turn | rewritten, rarely appended |
| knowledge | unbounded | map every turn, note on demand | appended per finding, dated |

The map is generated from each note's front matter, so it cannot drift from the
files. It refuses to grow past 3,000 characters and trims the oldest rows instead,
which makes the map's size a visible budget rather than a slow leak.

## Note format

```markdown
---
title: MoE expert caching
answers: merged expert cache is a loss on this machine
updated: 2026-10-22
tags: [moe, cache, speed]
---

# MoE expert caching

**Answer.** One or two sentences that settle the question.

## Evidence
- 2026-10-21: cache 0 = 36-37.5 t/s, 4096 MiB = 24-24.5 t/s (four runs each).

## What it rules out
The merged cache, at every size tested.

## Open
The unmerged GPU-graph branch was not built.
```

`answers` is what appears in the map; without it the note is not indexed and
`kb.py lint` fails.

## Install

```powershell
git clone <repo> E:\AI\jarvis
cd E:\AI\jarvis
python kb.py index
python kb.py lint
```

Personal notes are not in the repo (see `.gitignore`). Start from `examples/`:

```powershell
Copy-Item examples\knowledge\* knowledge\
Copy-Item examples\memory\* memory\
python kb.py index
```

### Hermes

```powershell
.\adapters\hermes\install.ps1            # backs up the old hook, installs a shim
```

The hook reads `JARVIS_HOME` (default `E:\AI\jarvis`), so moving the repo means
changing one environment variable, not editing code.

### OpenCode

```powershell
Copy-Item .\adapters\opencode\knowledge-index.js $env:USERPROFILE\.config\opencode\plugins\
```

The plugin pushes a synthetic text part on `chat.message`, the same mechanism the
`opencode-mem` plugin uses.

## Commands

```text
python kb.py index                 rebuild the map
python kb.py lint                  structure + map consistency
python kb.py search "expert cache" search notes and memory
python kb.py show local-llm        print a note
python kb.py append local-llm "new measurement"   dated Evidence entry
python kb.py rmfact "wrong fact"   delete every line containing it
```

`rmfact` exists because a memory you cannot delete a fact from is not yours
(borrowed from JARVIS 4.0's memory panel).

## Design decisions

- **Files canonical, index derived.** A database is a cache here, never the only
  copy; it can be rebuilt from the notes at any time.
- **Injection by code, not discipline.** The map is re-sent every turn so it
  survives compaction; relying on the model to remember to read it fails.
- **Personal data stays out of git.** Only code, schemas and synthetic examples
  are tracked, matching the rule used by the PersonalMemory archive.
- **Adapters are replaceable.** Switching harness means writing one file that
  reads `INDEX.md`; the corpus does not move.

## Related work

The design note (`docs/DESIGN.md`) and the research note
(`docs/RESEARCH.md`) compare this with backtalk, AI Memory Vault, JARVIS 4.0 /
Mark-LVI, Hermes, OpenCode and the PersonalMemory archive, and record what was
taken from each.

## License

MIT for the code. Personal notes are the owner's and are not distributed.
