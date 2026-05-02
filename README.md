<p align="center">
  <img src="assets/hero-course.png" alt="agent-zero-to-hero · the course" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-89b4fa?style=flat-square" alt="MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10+-89b4fa?style=flat-square&logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/badge/tests-42_passing-a6e3a1?style=flat-square" alt="42 tests">
  <img src="https://img.shields.io/badge/api_keys_required-0-a6e3a1?style=flat-square" alt="0 API keys">
  <img src="https://img.shields.io/badge/frameworks-none-f38ba8?style=flat-square" alt="no frameworks">
  <img src="https://img.shields.io/badge/providers-anthropic_·_openai_·_gemini-cba6f7?style=flat-square" alt="3 providers">
</p>

# agent-zero-to-hero

> **A 7-week course in agent engineering. Build a Claude-Code-shaped CLI agent from one HTTP call to a working website builder. ~4,500 lines of Python. 19 chapters. Zero frameworks.**

<table>
<tr>
<td width="35%" valign="middle"><img src="assets/mascot-wave.gif" alt="GuiGui waving" width="100%"></td>
<td valign="middle">

### Hi! I'm GuiGui 🐢 — your TA for this course.

We're going to build a Claude-Code-shaped agent harness *together* — from one HTTP request all the way to a CLI that ships real software. **No frameworks. No magic.** Every primitive in your favorite coding agent — sessions, compaction, MCP, skills, streaming — you'll write yourself.

The course assumes you can write Python. That's it. By the end, you'll be able to read the source of Cursor, Claude Code, or Devin and recognize every primitive by name.

**Pick a chapter and let's go.** ↓

</td>
</tr>
</table>

---

## 🗺️ The 7-week journey

<p align="center">
  <img src="assets/journey.png" alt="The 7-week journey" width="100%">
</p>

| Week | Theme | Chapters |
|---|---|---|
| <img src="assets/week1.png" width="120"><br>**Week 1** | **Foundations.** From one HTTP call to the agent loop. | [00](chapters/ch00_welcome.md) · [01](chapters/ch01_raw_call.md) · [02](chapters/ch02_messages_array.md) · [03](chapters/ch03_stop_reasons.md) · [04](chapters/ch04_one_tool.md) · **[05](chapters/ch05_the_loop.md)** |
| <img src="assets/week2.png" width="120"><br>**Week 2** | **Tool engineering.** Parallel calls, errors, system prompts. | [06](chapters/ch06_parallel_tools.md) · [07](chapters/ch07_errors.md) · [08](chapters/ch08_system_prompts.md) |
| <img src="assets/week3.png" width="120"><br>**Week 3** | **Cost & observability.** The dollar ticker. The 5× cache lever. Compaction. | [08b](chapters/ch08b_observability.md) · **[08c](chapters/ch08c_prompt_caching.md)** · **[10](chapters/ch10_compaction.md)** |
| <img src="assets/week4.png" width="120"><br>**Week 4** | **Persistence & scale.** Sessions on disk. Subagents. | [09](chapters/ch09_sessions.md) · **[11](chapters/ch11_subagents.md)** |
| <img src="assets/week5.png" width="120"><br>**Week 5** | **Skills & MCP.** Markdown loaded on demand. Three JSON-RPC calls. | [12](chapters/ch12_skills.md) · **[13](chapters/ch13_mcp_wire.md)** · [14](chapters/ch14_mcp_agent.md) |
| <img src="assets/week6.png" width="120"><br>**Week 6** | **Engineering polish.** Streaming. Three providers, one loop. | [15](chapters/ch15_streaming_text.md) · [16](chapters/ch16_streaming_tools.md) · [17](chapters/ch17_multi_provider.md) |
| <img src="assets/week7.png" width="120"><br>**Week 7** | **Capstone.** Read [`agent.py`](agent.py). Run [`microsite/`](microsite/). Build something. | [agent.py](agent.py) · [microsite](microsite/) |

> **Bold chapters** are the load-bearing concepts — read those twice.
> Full schedule with problem sets, labs, and final exam in **[SYLLABUS.md](SYLLABUS.md)**.

---

## ⚡ Quick start

```bash
git clone https://github.com/KeWang0622/agent-zero-to-hero.git
cd agent-zero-to-hero
pip install -e .

# tests pass with NO API key — verify the install
pytest tests/                                          # 42 passed in 0.6s

# the rest needs ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY=sk-ant-...
python -m chapters.ch00_welcome "what is 17 * 23?"     # your first agent

# the climax: a Claude-Code-shaped CLI you understand line by line
python agent.py "build me Tetris in one HTML file and open it"

# the capstone: the agent you wrote ships a real website
python microsite/build_site.py "a Brooklyn ramen shop called Sazae"
```

---

## 🎬 The agent loop, in motion

<p align="center">
  <a href="assets/loop-anim.mp4"><img src="assets/loop.png" alt="The agent loop" width="80%"></a>
</p>

This is the entire shape of every coding agent. The model is stateless; the messages array is the only memory. Tools, skills, sessions, MCP — they're how the **harness** extends the model. They're not the agent. **The loop is.**

```python
# the entire agent loop. six lines. no abstractions.
while True:
    r = client.messages.create(model=M, messages=msgs, tools=TOOLS)
    msgs.append({"role": "assistant", "content": r.content})
    if r.stop_reason != "tool_use":
        return r
    msgs.append({"role": "user", "content": run_all_tools(r.content)})
```

By the end of [chapter 5](chapters/ch05_the_loop.md) you'll write this from memory.

---

## 📚 What you'll learn

Every concept in modern coding agents — explained, demonstrated, and built from scratch:

| Layer | Concepts | Chapters |
|---|---|---|
| **The loop** | stateless API · messages array · stop reasons · tool use · parallel calls · errors | [01-07](chapters/) |
| **Cost** | system prompts · the dollar ticker · 5× prompt caching · compaction | [08-10](chapters/) |
| **Scale** | sessions on disk · context-isolated subagents | [09, 11](chapters/) |
| **Extension** | skills as markdown · MCP from raw JSON-RPC | [12-14](chapters/) |
| **Polish** | SSE streaming · partial JSON tool args · multi-provider adapters | [15-17](chapters/) |
| **Climax** | a 840-line Claude-Code-shaped CLI · website builder capstone | [agent.py](agent.py) · [microsite/](microsite/) |

---

## 🧪 Tests, no API key required

Every chapter has tests. Mock LLMs verify control flow. The MCP tests spawn real subprocesses and exchange real JSON-RPC. **You can verify the entire repo before signing up for an API key.**

```
tests/test_agent.py          18 passed   # production harness
tests/test_smoke.py           6 passed   # agent.py end-to-end with mocks
tests/test_mcp_wire.py        4 passed   # real subprocess JSON-RPC
tests/test_multi_provider.py  5 passed   # adapter foot-guns
tests/test_agent_loop.py      4 passed   # mock-LLM control flow
tests/test_session.py         2 passed   # JSONL round-trip
tests/test_skills.py          3 passed   # SKILL.md parsing
                            ─────────
                            42 passed in 0.6s
```

---

## 📂 What's in the repo

```
chapters/        19 numbered Python files + matching .md walkthroughs
agent.py         the climax — 840-line Claude-Code-shaped CLI
microsite/       capstone — build a website from one prompt
skills/          example SKILL.md files (haiku-master, landing-page)
mcp_servers/     example MCP servers (calculator)
tests/           42 tests, no API key required
docs/            ADAPTING.md, FAQ.md, WISHLIST.md
SYLLABUS.md      7-week schedule with problem sets and exam
AGENT.md         project context auto-loaded by agent.py
```

---

## 🐢 Quotable mottos — one per hero chapter

| Chapter | Motto |
|---|---|
| [02 messages](chapters/ch02_messages_array.md) | *"The messages array IS the memory. There is no other memory."* |
| [05 the_loop](chapters/ch05_the_loop.md) | *"An agent loop is just `while True` of one talking to the other."* |
| [08c caching](chapters/ch08c_prompt_caching.md) | *"It's not a feature. It's a placement problem."* |
| [10 compaction](chapters/ch10_compaction.md) | *"Surgery, not GC. Replace the older half with one synthetic message."* |
| [11 subagents](chapters/ch11_subagents.md) | *"Context isolation as a feature. 10× cheaper."* |
| [13 mcp_wire](chapters/ch13_mcp_wire.md) | *"Three method calls. JSON-RPC over stdio. That's all."* |

---

## 🎓 For instructors

This course is MIT-licensed and built to be adopted. If you teach at a university, bootcamp, or run a study group:

- All chapters are runnable in 30 seconds. Tests run in 0.6s without API keys → CI-friendly.
- 25 students × 7 weeks ≈ $50 in API spend (the speedrun is ~$0.50; the capstone is ~$5–10).
- See [SYLLABUS.md](SYLLABUS.md) for problem sets, labs, and final exam.

[Open an issue](https://github.com/KeWang0622/agent-zero-to-hero/issues) to add your school to the README.

---

## 🤝 Notable ports

This repo wants to be ported. Open a PR adding yours:

| Language | Author | Repo |
|---|---|---|
| Python (canonical) | [@KeWang0622](https://github.com/KeWang0622) | this repo |
| _Rust?_ | _you?_ | _open a PR_ |
| _Go?_ | _you?_ | _open a PR_ |
| _TypeScript?_ | _you?_ | _open a PR_ |

---

## 🙏 Acknowledgements

- [@karpathy](https://github.com/karpathy) for `nanoGPT` / `nanochat` — the literary genre of educational repos.
- [Anthropic](https://anthropic.com) for shipping the cleanest tool-use protocol of any major LLM provider.
- [Simon Willison](https://simonwillison.net) — *"Claude Skills are maybe a bigger deal than MCP"* inspired chapter 12.

## License

MIT. See [LICENSE](LICENSE).
