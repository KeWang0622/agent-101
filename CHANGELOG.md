# Changelog

## v0.2.0 — production polish (2026-05-02)

### `agent.py` rewritten to production quality

What changed in the harness:

- **Streaming output via SSE.** Tool calls, text, and `input_json_delta` accumulation handled correctly. Real-time rendering — same UX as Claude Code.
- **Retries with full-jitter exponential backoff.** Survives 429 / 529 / network blips. `with_retries()` wraps every API call.
- **Live cost & token meter.** `Meter` tracks input / output / cache_read / cache_creation tokens; projects to USD with current Sonnet 4.5 prices. Status line after every turn. `/cost` slash command.
- **Prompt caching on system + tools.** ~10x reduction on input cost for multi-turn sessions. `AGENT101_NO_CACHE=1` to disable for debugging.
- **Auto-compaction at 60% of context window.** Honors the `tool_use` boundary (won't summarize a slice ending on an assistant tool_use, which the API rejects).
- **Crash recovery on `--resume`.** `Session.truncate_orphan_user()` drops orphan user messages from a previously-crashed turn so the resumed session is in a valid state for the next API call.
- **3 new slash commands.** `/cost` (token + USD), `/model` (current model), `/init` (create AGENT.md).
- **Edit diff rendering fixed.** Was using non-existent `[default]` rich color; now actual red/green unified diff.
- **TodoWrite persists** across turns on `session.todos`.
- **Graceful Ctrl-C** cancels the in-flight turn without losing the session.

### New chapter

- **ch08b_observability.py** — the dollar ticker, in 30 lines. The chapter the research said was the highest-leverage missing piece.

### Tests

- 18 new tests in `tests/test_agent.py`. Cover Meter math, Session orphan recovery, the compaction tool_use boundary, retry backoff, prompt caching wrappers, all 7 tools.
- Total: **36 tests, 0.58s, no API key required.**

### Lecture-quality CONCEPT.md walkthroughs

7 chapters now have long-form `.md` companions following the Karpathy/Ng-derived template (planted misconception → wrong version → right version → named failure → try-this → agent.py footer):

- ch01_raw_call.md
- ch02_messages_array.md
- ch04_one_tool.md
- ch05_the_loop.md
- ch10_compaction.md
- ch11_subagents.md
- ch13_mcp_wire.md

### Visual assets

- `assets/launch.tape` — vhs script for the launch GIF (uses `Wait+Line` patterns to track real model latency)
- `assets/README.md` — Figma recipe for the OG social preview (1280×640, Catppuccin Mocha, JetBrains Mono)

## v0.1.0 — initial release (2026-05-02)

- 18 chapters of progressive Python files
- agent.py — first cut of the Claude-Code-shaped CLI
- microsite/ — capstone (build a website from one prompt)
- 18 tests, MIT license, public on github.com/KeWang0622/agent-101
