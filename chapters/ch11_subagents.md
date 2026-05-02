# Chapter 11 — Subagents (Context Isolation as a Feature)

> **A subagent is an agent loop with a fresh `messages` array, called as a tool.
> Its conversation is invisible to the parent. Only its final answer comes back.**

## The hook

The dirty math of agent costs: **input tokens dominate**. A 30-turn coding session can have an output bill of $0.10 and an input bill of $4.00, because every turn re-ships the entire history. If you ask the parent agent "summarize the longest Python file in chapters/", and it does it itself, the parent's `messages` array fills up with 50KB of file contents you'll never reference again — and every subsequent turn pays for those 50KB.

A subagent fixes this in one move. You delegate the side quest to a child process (a fresh agent loop with its own `messages` array, its own tools, its own context). The child does the dirty work — reads the files, dispatches tools, fills its own context with junk. Then the child returns ONE STRING — the answer — to the parent. The parent's context grows by ~17 tokens instead of ~17,000.

This is the load-bearing trick behind Claude Code's `Task` tool, openclaw's `subagent`, and every "deep research" feature in 2026.

## What you already know

From ch05: an agent loop is `while True { call → dispatch → continue }`. From ch06: parallel tools batch into one user message. From ch10: compaction is one way to shrink context.

Subagents are another way: shrink context by *isolating* it.

## The wrong version

The naive way to handle big tasks: run the parent itself for 100 turns, watch context fill to 60%, trigger compaction, lose detail, repeat. Compaction is the GC pass; subagents are the *avoid generating garbage* pass. Compaction recovers context after damage; subagents prevent damage.

## The right version

Wrap a fresh `agent_loop` call inside a tool the parent can call:

```python
def run_subagent(task: str, system: str = "") -> str:
    msgs = [{"role": "user", "content": task}]
    final_text = ""
    for _ in range(20):
        r = client.messages.create(
            model=MODEL, max_tokens=2048,
            system=system or "You are a focused subagent. Be terse.",
            tools=SUBAGENT_TOOLS, messages=msgs)
        msgs.append({"role": "assistant", "content": r.content})
        final_text = "".join(b.text for b in r.content if b.type == "text")
        if r.stop_reason != "tool_use": break
        msgs.append({"role": "user", "content": [...tool_results...]})
    return final_text
```

That's it. The parent calls `run_subagent("find the longest python file")`, the child does its own loop with its own `msgs`, and only `final_text` flows back.

## Cost math

- **Single agent, no subagent**: ~50,000 input tokens × 10 turns = 500K tokens
- **Same problem with subagent**: parent ~5,000 input × 10 turns = 50K, plus subagent ~50,000 × 5 turns = 250K, but subagent's context dies with the call — net ≈ 300K
- **With prompt caching on the subagent's system prompt**: ~120K

10× cheaper. And the parent stays sharp because its context is uncluttered.

The Anthropic blog reports multi-agent workflows use 4–7× more tokens than single-agent — that's *without* prompt cache sharing. With cache sharing (Claude Code's `CLAUDE_CODE_FORK_SUBAGENT=1`), the math flips and subagents become net cheaper for the parent.

## What could go wrong

**The subagent token explosion.** Symptom: you spawn a subagent for every minor side quest, your bill triples. Cause: each subagent has its own startup cost (system prompt, tool definitions, "you are a subagent" preamble) — typically 2–5K tokens before it does any work. If your task is small (one tool call), the subagent overhead exceeds the savings.

Fix: only spawn subagents for tasks where the parent would otherwise dump >5K tokens into its context. A heuristic: if the parent would call >3 tools or read >2 files, delegate. Otherwise inline.

## Try this

```bash
python -m chapters.ch11_subagents
```

1. Watch the trace. Notice the indentation — parent and subagent traces are visually separated.
2. Print `len(parent_msgs)` after the subagent returns. Compare to running the same task without delegation. The parent's array should be tiny.
3. Add a second subagent — make the parent delegate two side quests *in parallel*. Watch the parent's context stay flat while two subprocesses do their own work.

## When NOT to use this

For small tasks (<3 tools), the subagent overhead exceeds the savings. For tasks where the parent NEEDS the intermediate context (e.g., the user said "remember everything you read"), don't delegate — the parent has to see it. Subagents are for *information you'll throw away*.

## Where this shows up in agent.py

`agent.py` has the seven core tools but doesn't ship a `Task` tool by default — adding one is the single most impactful extension you can make to the harness. Take `run_subagent()` from this chapter, register it in `TOOLS` and `DISPATCH`, and you've added Claude Code's most powerful feature in 30 lines.

## Going deeper

- [Anthropic — How we built Claude Code's subagent system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [`learn-claude-code` s04](https://github.com/shareAI-lab/learn-claude-code) — fresh-`messages[]` subagent pattern
- [The subagent token explosion (AICosts.ai)](https://www.aicosts.ai/blog/claude-code-subagent-cost-explosion-887k-tokens-minute-crisis) — the cost math written out at production scale
