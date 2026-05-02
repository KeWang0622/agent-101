# Launch playbook

Templates for launching agent-101. Use these on Day 0; do not deviate.

## Twitter thread (9 tweets)

**Tweet 1** — the hook + ONE image (terminal screenshot of `agent.py` running tetris demo):
```
agent-101: build a Claude Code-shaped agent harness from scratch.

18 chapters of Python.
~2000 lines.
no LangChain, no graph DSL, no framework magic.
just the loop:

[image: 6-line agent loop]
```

**Tweet 2** — what it is + repo link:
```
each chapter is one .py file teaching one concept:
ch05 — the canonical 6-line agent loop
ch10 — compaction (the chapter everyone googles)
ch13 — MCP demystified (it's just JSON-RPC over stdio)
ch17 — the same loop, three providers (anthropic / openai / gemini)

github.com/KeWang0622/agent-zero-to-hero
```

**Tweet 3** — why:
```
everyone uses claude code, cursor, devin.
almost nobody can explain what they actually do.
this repo is the answer.

after 18 chapters, you can read claude code's source and recognize every
primitive by name.
```

**Tweet 4** — tests:
```
every chapter has tests. zero require an API key.

mock LLMs verify control flow.
real subprocesses verify the MCP wire.
the multi-provider tests catch the foot-guns
(openai's json-string args, gemini's missing tool stop reason).

pytest tests/ — 18 passed in 0.5s.
```

**Tweet 5** — the climax:
```
chapter 17 ends with you having written agent.py — a ~600-line
Claude-Code-shaped CLI. it streams. renders tool calls in boxes. shows
diffs. persists sessions to disk. asks before it touches anything.

then you use it to build a working website from one prompt.
```

**Tweet 6** — the capstone (with GIF if possible):
```
$ python microsite/build_site.py "a Brooklyn ramen shop called Sazae"

→ planning... 4 todos
→ writing index.html
→ opening in browser

[GIF of the landing page rendering]

the agent you just built ships real software.
```

**Tweet 7** — anti-framework:
```
this isn't a framework. don't `pip install`.
read it. copy it. throw it away.

if you understand what's in chapter 5, you understand what cursor is.
if you understand chapter 10, you understand why claude code works for an
hour and chatgpt for 10 minutes.
```

**Tweet 8** — port invitation:
```
ports welcomed. open a PR adding yours to the README:

| Language | Author | Repo |
| python (canonical) | @KeWang0622 | this repo |
| your port? | you? | open a PR |

llm.c got llm.cpp / llm.zig / llm.rs by asking.
```

**Tweet 9** — credits + thanks:
```
inspired by:
@karpathy's nanoGPT/nanochat — the literary genre of educational repos
@simonw's "Claude Skills are maybe a bigger deal than MCP" — chapter 12
the openclaw team — the open clone that documents the patterns

read the repo: github.com/KeWang0622/agent-zero-to-hero
```

## Hacker News title (NO "Show HN")

```
Agent-101: Build an agent harness from scratch in 18 chapters
```

## Reddit

**r/LocalLLaMA**:
```
Agent-101: a from-scratch agent harness (raw API calls, no LangChain)
```

**r/MachineLearning** (uses [P] tag):
```
[P] Agent-101 — from-scratch educational agent harness in the nanochat lineage
```

**r/ClaudeAI**:
```
I built a 'nanochat for agents' using raw Anthropic API — open source
```

## Day-by-day timeline

**Day 0 (Tuesday or Wednesday, 14:00-16:00 UTC)**:
- Twitter thread
- HN submission (5 min after tweet 1)
- First-comment your own HN post within 5 minutes
- r/LocalLLaMA post
- Reply to every HN comment for 4 hours straight
- DO NOTHING ELSE. HN punishes coordinated promotion.

**Day 1 (Wednesday)**:
- LinkedIn post 13:00 UTC
- r/ClaudeAI post
- TLDR AI / Ben's Bites submissions

**Day 2**: rest. Reply to issues + PRs.

**Day 3**:
- dev.to article
- r/MachineLearning [P] post
- Discord posts (Anthropic, MCP, Latent Space)

**Day 5**: follow-up tweet thread with launch numbers + lessons learned

**Day 7**: cold-pitch creators (Yannic Kilcher, Matthew Berman, AI Jason)

**Week 2**: ship v0.2 with the most-requested feature

## Don't

- Tag @karpathy / @AnthropicAI in tweet 1 (mute-bait)
- Ask for HN upvotes anywhere (HN flags this)
- Cross-post to >1 subreddit on Day 0
- Use hashtags on Twitter
- Post on a Friday or weekend
- Get into LangChain flamewars in comments
