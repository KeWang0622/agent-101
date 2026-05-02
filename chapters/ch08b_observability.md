# Chapter 08b — Observability: The Dollar Ticker 🐢

> **The #1 surprise for new agent builders is bill shock. Your agent runs 8 turns and costs $0.40. A meter is 30 lines.**

## 🐢 GuiGui says

Most "build an agent" tutorials skip cost. That's why so many demos die at 3am of the launch night. Read `response.usage` after every turn. Multiply by prices. Print. Done.

## The idea

Four `usage` fields:

```python
usage.input_tokens                  # full input to this call
usage.output_tokens                 # text + tool_use produced
usage.cache_creation_input_tokens   # tokens written to cache
usage.cache_read_input_tokens       # tokens read from cache (90% cheaper)
```

## Show me the code

```python
PRICES = {"input": 3.00, "output": 15.00, "cache_w": 3.75, "cache_r": 0.30}

def cost(u):
    return ((u.input_tokens   * PRICES["input"]
           + u.output_tokens  * PRICES["output"]
           + (u.cache_creation_input_tokens or 0) * PRICES["cache_w"]
           + (u.cache_read_input_tokens or 0)     * PRICES["cache_r"])
           / 1_000_000)

# print after every turn
print(f"turn {turn}: ${cost(r.usage):.4f}")
```

## ⚠️ Watch out for

**The silent zero.** Wrap `system` in `cache_control` but `cache_read` stays 0. Cause: prompt below 1024 tokens (Sonnet) — caching silently doesn't engage. See [ch08c](ch08c_prompt_caching.md).

## ✅ Summary

- `response.usage` tells you exactly what each call cost.
- 4 fields × current prices = USD per turn.
- Print live. The total adds up faster than you'd guess.

## 📝 Homework

```bash
python -m chapters.ch08b_observability "what is 17 * 23?"
```

1. Run a 30-turn task. What was the total cost?
2. Compute cache hit ratio: `cache_read / (cache_read + cache_create)`.
3. Find your most expensive turn. Why was it expensive?

## 🚀 Next

[Chapter 08c — Prompt caching deep dive](ch08c_prompt_caching.md): the 5× cost lever.
