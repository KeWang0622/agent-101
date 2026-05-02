# Chapter 08c — Prompt Caching, Deep 🐢

<p align="center">
  <img src="../assets/ch08c-illustration.png" alt="Prompt caching" width="100%">
</p>

> **Caching is the single biggest cost lever for agents. Get it right: 5× cheaper. Get it wrong: pay the cache *write* price every turn AND never read.**

## 🐢 GuiGui says

This isn't a feature you "turn on." It's a placement problem: WHERE do you put `cache_control`? Three rules and you're set. Skip them and caching is silently a no-op.

## The 3 rules

**Rule 1 — The threshold.** Below the minimum, `cache_control` is silently ignored.

| Model | Minimum input |
|---|---|
| Sonnet / Opus | 1,024 tokens |
| Haiku | 2,048 tokens |

**Rule 2 — The breakpoints.** Up to 4 `cache_control` markers per request. Each marks the END of a cacheable prefix. Order: cache the things that change LEAST.

**Rule 3 — The TTL.** Default = 5 min. Daemons should use 1h (`{"type": "ephemeral", "ttl": "1h"}`) — 2× write cost, 12× lifetime, break-even ~12 calls.

## Show me the code

```python
# cache the system prompt + the entire tools list
system = [{"type": "text", "text": SYSTEM,
           "cache_control": {"type": "ephemeral"}}]

# put cache_control on the LAST tool — caches everything up to it
tools = [*TOOLS_LIST[:-1],
         {**TOOLS_LIST[-1], "cache_control": {"type": "ephemeral"}}]

r = client.messages.create(model=M, system=system, tools=tools,
                           messages=msgs, max_tokens=1024)
```

## Cache by demonstration (real measured data)

```
run 1, no cache:    $0.0055   in=1589   cw=0      cr=0
run 2, no cache:    $0.0052   in=1589   cw=0      cr=0
run 3, cache write: $0.0065   in=13     cw=1576   cr=0     ← writes
run 4, write hit:   $0.0072   in=13     cw=1576   cr=0
run 5, full read:   $0.0010   in=13     cw=0      cr=1576  ← 5× cheaper
```

## ⚠️ Watch out for

**The cache poisoning.** Embedding `datetime.now()` in your system prompt → cache miss every turn → you pay the write price (1.25×) AND never read. Cache the stable prefix. Vary the tail.

## ✅ Summary

- Below 1024 tokens (Sonnet), caching is silent no-op.
- `cache_control` marks the END of the cacheable prefix.
- 5× cost reduction is real. We've measured it. Run 5 vs run 1.

## 📝 Homework

```bash
python -m chapters.ch08c_prompt_caching
```

1. Watch run 5 vs run 1. Confirm 5× delta.
2. Make the system prompt 500 tokens (below threshold). Confirm `cache_read` stays 0.
3. Compute break-even: at what call count does 1h TTL beat 5m TTL? (Hint: 2× write, 12× lifetime.)

## 🚀 Next

[Chapter 09 — Sessions](ch09_sessions.md): a conversation that survives `Ctrl-C`.
