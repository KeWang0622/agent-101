# Chapter 05 — The Loop

> **The thing the model can't do is run code. The thing you can't do is think.
> An agent loop is just `while True` of one talking to the other.**

## The hook

The first time I wrote an agent loop, it printed *"I'll check the file for you"* — and then stopped. Just stopped. No error. No file read. Nothing. I stared at the trace for ten minutes before I understood: I had called the model exactly once, dispatched the tool it asked for, and never called the model again with the result. Claude said *"I'll check,"* and I had given it no chance to actually check. An agent isn't a function call. It's a conversation. And conversations need a second turn.

## What you already know

From `ch04_one_tool.py`: one round-trip is `tool_use` → run it → `tool_result` → final answer. Two API calls, hard-coded. Now we want **N**.

## The wrong version

The naive fix: a fixed two-call sequence. Run it on *"what's the biggest Python file in chapters/?"* and watch it break — the model calls `glob` on turn 1, gets a file list, and your code returns. The model never gets a chance to call `read_file` to actually count lines. **Two-call sequences only work for one-step problems.** The general case needs an unbounded number of turns.

## The right version

Six lines:

```python
while True:
    r = client.messages.create(model=M, messages=msgs, tools=TOOLS)
    msgs.append({"role": "assistant", "content": r.content})
    if r.stop_reason != "tool_use":
        return r
    msgs.append({"role": "user", "content": run_all_tools(r.content)})
```

Read it slowly. The model is *stateless* — every call sends the entire `msgs` array. *You* are the state-holder; the model just transforms one messages array into the next. The loop ends when the model stops asking for tools (`stop_reason != "tool_use"`). Otherwise we run every tool the model asked for and append the results as a single user message — never one user message per tool, always one user message containing all tool_result blocks.

That last sentence is the rule that catches most beginners. Chapter 6 will show you what breaks if you violate it.

## The mental model

```
   you ──user msg──> [model] ──assistant msg (text + tool_use)──> you
                        ^                                           │
                        │                                           │
                        └────user msg (tool_result blocks)──────────┘
```

Two-character protocol. Forever.

## What could go wrong

**The runaway loop.** Symptom: the agent calls the same tool with the same args 50 times, your bill becomes $40 in an hour, you find out at 3am. Fix: replace `while True` with `for turn in range(MAX_TURNS)`. We use `MAX_TURNS = 25` in this chapter; production harnesses use 50–100. Whatever the cap, **you must have one.** Without it, a single misbehaving prompt can cost real money before you notice.

The cause: a tool that returns "you should call me again" forever. Sometimes a buggy tool, sometimes a stuck retrieval, sometimes the model just gets confused. The cap is your circuit breaker.

## Try this

Run `ch05_the_loop.py` and watch the trace:

1. `python -m chapters.ch05_the_loop "what's the biggest python file in chapters/?"` — count how many turns it takes.
2. Add `print(f"turn {turn}: msgs.len={len(msgs)}")` inside the loop. Watch the array grow.
3. Lower `MAX_TURNS = 3` and run a complex query. Watch the cap save you.

## When NOT to use this

If your task is one-shot ("translate this paragraph"), the loop is overkill — use `ch01_raw_call.py`'s pattern. The loop is for tasks that require the model to *gather information it doesn't yet have*.

## Where this shows up in agent.py

Lines 487–540, the `agent_turn` function. Same six lines, with streaming added (ch15), retries with exponential backoff wrapped around the API call (production), and approval prompts wrapped around tool dispatch.

## Going deeper

- Anthropic — [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- Karpathy — [Software 3.0](https://www.youtube.com/watch?v=LCEmiRjPEtQ) on the agent loop as a fundamental primitive
- Read `agent.py` — your loop, in production form
