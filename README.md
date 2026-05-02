# agent-101

**Build a Claude-Code-shaped agent harness from scratch.**
*18 chapters · ~3,000 lines of Python · 3 LLM providers · 36 tests · zero frameworks.*

Everyone uses Claude Code, Cursor, Devin. Almost nobody can explain what they actually do under the hood. This repo is the answer.

```
              ┌──────────────────┐
              │  messages array  │   ◀── ch02 · the only memory
              │  [user, asst,…]  │
              └────────┬─────────┘
                       │ send full history every turn (stateless API)
                       ▼
   ┌──────────┐   ┌─────────────────────┐   ┌─────────────────┐
   │  skills  │──▶│                     │◀──│  tools          │
   │  ch12    │   │   claude / openai   │   │ Read · Bash     │
   │  MD on   │   │   / gemini          │   │ Edit · Glob     │
   │  demand  │   │                     │   │  ch04–06        │
   └──────────┘   │   (the model)       │   └─────────────────┘
                  │                     │
   ┌──────────┐   │                     │   ┌─────────────────┐
   │  MCP     │──▶│                     │◀──│ session (jsonl) │
   │ ch13–14  │   │                     │   │  ch09           │
   │ stdio    │   └──────────┬──────────┘   │ append-only     │
   │ JSON-RPC │              │              └─────────────────┘
   └──────────┘              │ stop_reason
                             ▼
                      ┌─────────────┐
                      │  tool_use?  │── no ──▶ return to user
                      └──────┬──────┘
                             │ yes
                             ▼
                      run_all_tools()  ─── results back to messages ──┐
                             │                                         │
                             └─────────────────────────────────────────┘
                                         the loop · ch05
```

Every agent product on the market is this picture. The model is stateless; the messages array is the only memory. Tools, skills, sessions, MCP — they're how the **harness** extends the model. They're not the agent. The loop is. By ch05 you've written it in 6 lines. By ch17 you've written every box around it. By the climax (`agent.py`), you've assembled all of it into a working CLI that actually ships software.

Eighteen short chapters that build an agent harness — the agent loop, tool use, parallel calls, errors, sessions, compaction, sub-agents, skills, MCP — directly against the raw HTTP API. By the end you have a single ~600-line `agent.py` that runs in your terminal, streams output, edits files, executes bash, persists sessions to disk, and asks before it touches anything. Then you use that agent to build a working website from one prompt.

No LangChain. No CrewAI. No graph DSL. Just the loop.

```python
# the entire agent loop, no abstractions
while True:
    r = client.messages.create(model=M, messages=msgs, tools=TOOLS)
    msgs.append({"role": "assistant", "content": r.content})
    if r.stop_reason != "tool_use":
        return r
    msgs.append({"role": "user", "content": run_all_tools(r.content)})
```

That's the whole pattern. Six lines. Every framework on Earth is wrapped around them. By chapter 5 you've written this yourself; by chapter 18 you've added 600 lines of UX, sessions, skills, and MCP around it; and you can read Claude Code's source and recognize every primitive by name.

## The numbers

- **18 chapters** • each one a single Python file • runnable in <30 seconds
- **~2,000 lines** of Python end-to-end • zero framework dependencies
- **3 LLM providers** supported via a 100-line adapter (Anthropic, OpenAI, Gemini)
- **18 tests** • no API key required • `pytest tests/` passes in 0.5s

## First 5 minutes

If you only do three things:

1. Read [`chapters/ch05_the_loop.py`](chapters/ch05_the_loop.py) — 125 lines. The 6 lines that are every agent.
2. Run `python agent.py "build me Tetris as one HTML file"` — see your loop ship something real.
3. Read [`agent.py`](agent.py) — 505 lines. Every primitive from chapters 1–17, integrated.

That's it. Everything else in this README is optional context.

## Quick start

```bash
git clone https://github.com/KeWang0622/agent-101.git
cd agent-101
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...

# run every chapter end-to-end (~10 min, ~$0.50 in API calls)
bash runs/speedrun.sh

# or work through individually
python -m chapters.ch00_welcome "what's 17*23 then read README.md"
python -m chapters.ch01_raw_call
# ...all the way to ch17

# the climax: the Claude-Code-shaped CLI you just built
python agent.py "build me Tetris as one HTML file and open it"

# the capstone: build a website with the agent you wrote
python microsite/build_site.py "a Brooklyn ramen shop called Sazae"

# tests pass without an API key (mock LLM + real MCP subprocess)
pytest tests/
```

## The chapters

Read in order. Each is one concept. Each is runnable.

| # | Chapter | What you learn |
|---|---|---|
| 00 | [welcome](chapters/ch00_welcome.py) | A working agent in 30 lines. Read this once before anything else. |
| 01 | [raw_call](chapters/ch01_raw_call.py) | One HTTP POST. The Messages API, no SDK. |
| 02 | [messages_array](chapters/ch02_messages_array.py) | The API is stateless. The messages array IS the memory. |
| 03 | [stop_reasons](chapters/ch03_stop_reasons.py) | The four ways out: end_turn, tool_use, max_tokens, stop_sequence. |
| 04 | [one_tool](chapters/ch04_one_tool.py) | The tool_use → tool_result protocol. One round-trip. |
| 05 | **[the_loop](chapters/ch05_the_loop.py)** | The canonical 6-line agent loop. The course pivots here. |
| 06 | [parallel_tools](chapters/ch06_parallel_tools.py) | Multiple tool_use blocks in one turn. The single-user-message rule. |
| 07 | [errors](chapters/ch07_errors.py) | Tool errors as content. `is_error: true`. Refusals. |
| 08 | [system_prompts](chapters/ch08_system_prompts.py) | What goes in `system` vs `messages`. Prompt caching. |
| 08b | [observability](chapters/ch08b_observability.py) | The dollar ticker — `response.usage` × prices = no bill shock. |
| 09 | [sessions](chapters/ch09_sessions.py) | JSONL on disk. Resume after ctrl-c. |
| 10 | **[compaction](chapters/ch10_compaction.py)** | When the messages array gets too big, summarize and continue. |
| 11 | [subagents](chapters/ch11_subagents.py) | Context isolation as a feature. The Task meta-tool. |
| 12 | [skills](chapters/ch12_skills.py) | Markdown loaded on demand. Progressive disclosure. |
| 13 | **[mcp_wire](chapters/ch13_mcp_wire.py)** | MCP demystified — JSON-RPC over stdio with three method calls. |
| 14 | [mcp_agent](chapters/ch14_mcp_agent.py) | Wire your own MCP server into the loop. |
| 15 | [streaming_text](chapters/ch15_streaming_text.py) | SSE basics. Render text deltas as they arrive. |
| 16 | [streaming_tools](chapters/ch16_streaming_tools.py) | `input_json_delta` accumulation. The hard chapter. |
| 17 | [multi_provider](chapters/ch17_multi_provider.py) | Same loop, three wires (Anthropic / OpenAI / Gemini). |
| ★ | **[agent.py](agent.py)** | The Claude-Code clone. Six tools, slash commands, sessions, AGENT.md. |
| ★ | **[microsite](microsite/)** | The capstone. Build a working website from one prompt. |

Bold chapters are the hero ones — read them twice.

## Why this exists

Most "build an agent" tutorials teach you a framework. You learn LangChain or LangGraph or CrewAI. You learn an abstraction for an abstraction.

This repo teaches you what's underneath the abstraction. **The loop.** Once you've written it yourself, every agent product on the market becomes legible. Cursor is a fancier version of `agent.py`. Devin is `agent.py` with more tools and a better prompt. Claude Code is `agent.py` with a thousand more lines of polish.

The pedagogy: each chapter introduces ONE concept, with one runnable demo, in one Python file. You can read any chapter in 5 minutes and run it in 10 seconds. By chapter 5 you've written the agent loop. By chapter 12 you understand skills. By chapter 14 you've written your own MCP server. By chapter 18 you have a working CLI agent that you fully understand.

There are no abstractions to memorize, no providers to configure, no graph DSL. Each chapter is one Python file you can read in 5 minutes and modify in 10. By the end you will not have learned "an agent framework" — you will have built the harness yourself.

## What you get in `agent.py`

A production-shaped harness in one file:

| Feature | Where |
|---|---|
| Streaming output (SSE, chunk-buffered) | `stream_one_turn` |
| 7 tools: Read · Write · Edit · Bash · Glob · Grep · TodoWrite | `TOOLS` + `DISPATCH` |
| Tool-call rendering (●, ⎿, colored diffs for Edit) | `render_tool_call`, `render_tool_result` |
| JSONL session persistence + `--resume <id>` | `Session` |
| Crash recovery (orphan-user-message detection) | `truncate_orphan_user` |
| AGENT.md auto-discovery (walks up from cwd) | `load_agent_md` |
| Permissions: ask · allow · deny modes | `ask_permission` |
| Auto-compaction at 60% of context window | `compact_messages` |
| Retries with full-jitter exponential backoff | `with_retries` |
| Prompt caching on system + tools (5-min TTL) | `_build_system_param`, `_build_tools_param` |
| Live cost & token meter | `Meter` |
| 7 slash commands: `/help` `/cost` `/model` `/init` `/clear` `/compact` `/exit` | `handle_slash` |
| Graceful Ctrl-C handling | `agent_turn` |

This is not a sprint demo — it's a real harness. 800 LOC, every line readable, 18 dedicated tests in `tests/test_agent.py`.

## What the agent looks like

```
$ python agent.py
╭─ agent-101 • session a3f7b9c2d1e4 ─╮
│ model claude-sonnet-4-5 • cwd ~/code/myproject │
╰─────────────────────────────────────╯
> add a hello-world function to src/main.py and run it

I'll read the file first to see the structure.

● Read(src/main.py)
  ⎿  def main():
  ⎿      pass

● Edit(src/main.py)
  ⎿  + def hello():
  ⎿  +     print("hello, world")

● Bash$ python src/main.py
allow Bash$ python src/main.py? [Y/n] y
  ⎿  hello, world

Done — added `hello()` and ran it.
```

## File structure

```
agent-101/
├── README.md                    you are here
├── AGENT.md                     loaded by agent.py at startup (project context)
├── agent.py                     ★ the Claude-Code clone, ~600 LOC, all primitives
├── pyproject.toml               deps: anthropic, rich, httpx, pytest
├── chapters/
│   ├── ch00_welcome.py          a 30-line working agent (run me first)
│   ├── ch01_raw_call.py         one urllib.urlopen, no SDK
│   ├── ch02_messages_array.py   the stateless API revelation
│   ├── ch03_stop_reasons.py     end_turn / tool_use / max_tokens / stop_sequence
│   ├── ch04_one_tool.py         tool_use → tool_result, one round-trip
│   ├── ch05_the_loop.py         ★ the canonical 6-line loop
│   ├── ch06_parallel_tools.py   parallel calls, single-user-message rule
│   ├── ch07_errors.py           is_error=true, the foot-guns
│   ├── ch08_system_prompts.py   system vs messages, prompt caching
│   ├── ch09_sessions.py         append-only JSONL persistence
│   ├── ch10_compaction.py       ★ the chapter that pays for itself
│   ├── ch11_subagents.py        context isolation via the Task tool
│   ├── ch12_skills.py           SKILL.md, progressive disclosure
│   ├── ch13_mcp_wire.py         ★ three JSON-RPC calls demystify MCP
│   ├── ch14_mcp_agent.py        wire MCP into the agent loop
│   ├── ch15_streaming_text.py   SSE, render as you receive
│   ├── ch16_streaming_tools.py  input_json_delta accumulation
│   └── ch17_multi_provider.py   Anthropic / OpenAI / Gemini adapters
├── skills/
│   ├── haiku-master/SKILL.md    example skill loaded by ch12 / agent.py
│   └── landing-page/SKILL.md    used by the microsite capstone
├── mcp_servers/
│   └── calculator_server.py     ~80-line MCP server over stdio
├── microsite/
│   ├── build_site.py            ★ capstone: build a landing page from one prompt
│   └── README.md                
└── tests/
    ├── test_agent_loop.py       loop control flow with a mock LLM
    ├── test_session.py          JSONL round-trip
    ├── test_skills.py           skill discovery + parsing
    ├── test_multi_provider.py   adapter normalization
    └── test_mcp_wire.py         real subprocess, real JSON-RPC
```

## Tests, no API key

```bash
pytest tests/ -v
# 18 passed in 0.5s
```

**36 tests, 0.5 seconds, no API key.** Mock LLMs verify the loop's control flow. The MCP tests spawn real subprocesses and exchange real JSON-RPC. The multi-provider tests verify the foot-guns (OpenAI's JSON-string args, Gemini's missing tool stop reason). The agent tests verify the Meter math, Session orphan recovery, the compaction tool_use boundary, retry backoff, prompt caching wrappers, and every individual tool. You can clone the repo, run the tests, and confirm everything works before you sign up for an API key.

```
tests/test_agent.py          18 passed   # production harness
tests/test_agent_loop.py      4 passed   # mock-LLM control flow
tests/test_mcp_wire.py        4 passed   # real JSON-RPC subprocess
tests/test_multi_provider.py  5 passed   # adapter foot-guns
tests/test_session.py         2 passed   # JSONL round-trip
tests/test_skills.py          3 passed   # SKILL.md parsing
                             ─────────
                             36 passed in 0.58s
```

This is rare — most agent tutorials have empty `tests/` directories.

## What's NOT in this repo

- ❌ A framework. There is no `pip install agent-101`. Read it. Copy it. Throw it away.
- ❌ Hidden complexity. Every line is in front of you.
- ❌ Production hardening. This is a textbook, not a product.
- ❌ Vendor lock-in. The same loop runs on Anthropic, OpenAI, or Gemini. Same six lines.
- ❌ A Discord. If you have a question, the source code is the answer.

## Compared to other "build an agent" repos

| Repo | Stars | Language | What it teaches | What it skips |
|---|---|---|---|---|
| [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) | 57k | Python | 12 sessions • compaction • skills | streaming • tests • MCP-from-scratch |
| [sanbuphy/nanoAgent](https://github.com/sanbuphy/nanoAgent) | 574 | Python | the agent loop in 100 lines | sessions, compaction, skills, MCP, subagents |
| [baby-llm/baby-agent](https://github.com/baby-llm/baby-agent) | 359 | Go | MCP wire format • RAG | English-readability, Python audience |
| **agent-101** | — | **Python** | **all of the above + tests + multi-provider** | nothing — this is the textbook |

## Docs

- [docs/ADAPTING.md](docs/ADAPTING.md) — port to OpenAI or Gemini, the foot-guns explained
- [docs/FAQ.md](docs/FAQ.md) — three questions every reader asks
- [docs/LAUNCH.md](docs/LAUNCH.md) — launch playbook (templates for the launch tweet, HN title, subreddits)

## Acknowledgements

- [@karpathy](https://github.com/karpathy) for the nano-* template that made educational repos a literary genre.
- The [openclaw](https://github.com/openclaw/openclaw) team for the open clone of Claude Code that documents the patterns this repo distills.
- [Anthropic](https://anthropic.com) for shipping the cleanest tool-use protocol of any major LLM provider.
- [Simon Willison](https://simonwillison.net) whose "Claude Skills are maybe a bigger deal than MCP" tweet inspired chapter 12.

## Notable ports

This repo is meant to be ported. Open a PR and add yours here:

| Language | Author | Repo |
|---|---|---|
| Python (canonical) | [@KeWang0622](https://github.com/KeWang0622) | this repo |
| _your port?_ | _you?_ | _open a PR_ |

## License

MIT. See [LICENSE](LICENSE).
