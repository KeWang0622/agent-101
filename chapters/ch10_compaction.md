# Chapter 10 — Compaction

> **When the messages array gets too big, claude gets dumber AND more expensive.
> Compaction is one LLM call that summarizes old turns and lets you keep going.**

## The hook

Every Claude Code user has watched *"Compacting…"* appear and wondered what it actually does. Most assume it's a clever GC over hidden state. It's not. **Compaction is surgery.** You take your `messages` array, ask Claude to summarize the older half into a paragraph, throw away the original messages, and slot the paragraph in as a single user message. The conversation continues. The model has no idea anything happened — to it, the summary is just a long user turn from earlier.

This is the chapter that pays for itself. After this, you can run agents for hours on a 200K-token model without ever blowing the window.

## What you already know

From `ch02_messages_array.py`: the array grows by 2 per turn. From `ch04_one_tool.py` and `ch05_the_loop.py`: a single tool result can be 4KB. Multiply: a 30-turn coding session is 50–100KB of message history, easily 30K input tokens *per call*. The more you append, the slower and dumber and more expensive every turn becomes.

## The wrong version

The naive fix: drop the oldest N messages. Run a 30-turn coding session, drop the first 10 messages, and watch the agent forget that you asked it to *not* edit `prod/`. You've discarded the context that mattered most.

The second naive fix: summarize and prepend, but keep editing the original array. Now you have BOTH the summary AND the original messages — your context grew instead of shrinking.

The right move is to **replace the older portion with one synthetic message**, in place. The summary becomes the messages you no longer have.

## The right version

```
BEFORE (60% of context window — claude is getting dumb)
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ m1 │ m2 │ m3 │ m4 │ m5 │ m6 │ m7 │ m8 │ m9 │m10 │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
└──────── summarize via 1 LLM call ──────┘  keep recent ─┐
                       │                                  │
                       ▼                                  │
AFTER                                                     │
┌────────────────────────────────┐  ┌────┬────┬────┬────┐
│ <conversation_summary>          │  │ m7 │ m8 │ m9 │m10 │
│  did A, found B (id=42),       │  │    │    │    │    │
│  decided D, file=src/x.py …   │  │    │    │    │    │
│ </conversation_summary>        │  │    │    │    │    │
└────────────────────────────────┘  └────┴────┴────┴────┘
   one user message, ~800 tokens     verbatim, load-bearing
```

Four design choices that matter:

1. **Trigger** — token count, not message count. Use `client.messages.count_tokens()` to ask the API. Compact at 60% of the model's window: by 70% performance noticeably degrades.
2. **What to summarize** — the *oldest* N messages. Recent ones are still load-bearing.
3. **What to preserve** — file paths, UUIDs, URLs, decisions, pending TODOs. Anthropic's own summarizer prompt names these explicitly.
4. **What to drop** — retried tool results, idle exploration, errors that were resolved.

## What could go wrong

**The orphan tool_use.** Symptom: the API rejects your next call with `"tool_use ids ... did not have corresponding tool_result blocks"`. Cause: you summarized a slice that ENDED on an assistant `tool_use` block, leaving the matching `tool_result` in the recent slice — but the assistant message is now gone. The API requires the pair to be intact.

Fix: when picking the boundary, walk backwards until the older slice ends on a "safe" message (text-only assistant or user turn). `agent.py` does this at lines 425–429 — it shifts trailing tool_use turns into the recent slice rather than summarize them away.

## Try this

```bash
python -m chapters.ch10_compaction
```

The chapter's `stress_test()` stuffs the array until compaction triggers, then prints before/after token counts. Three things to notice:

1. The *summary length* (~800 tokens) vs the *original tokens* (~50K). 60x compression, and the next turn costs 1/60th.
2. The *KEEP_RECENT* default of 4. Lower it to 2 and watch the agent get amnesic. Raise to 10 and watch compaction barely help.
3. Edit the `SUMMARIZER_PROMPT` to drop the "preserve identifiers" line. Re-run a multi-step task. Watch UUIDs go missing from the summary. Then put the line back.

## When NOT to use this

For short-lived agents (under 10 turns), compaction is wasted overhead — the summarizer call costs more than the few turns it would save. Threshold: enable compaction when a session typically runs 20+ turns.

## Where this shows up in agent.py

- Lines 421–448, `compact_messages()` — including the tool_use boundary fix
- Lines 504–512 in `agent_turn()` — auto-compaction every 5 turns when context > 60%
- The `/compact` slash command, lines 700–704 — manual trigger

## Going deeper

- Anthropic — [Long-context tips](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) (the same doc covers compaction strategies)
- Read [openclaw's compaction.ts](https://github.com/openclaw/openclaw) — production version with token-budget trigger and 3 fallback tiers
- Hamel Husain — ["I tracked every token my coding agent consumed"](https://dev.to/nicolalessi/i-tracked-every-token-my-ai-coding-agent-consumed-for-a-week-70-was-waste-465) — 70% of agent spend is preventable with compaction
