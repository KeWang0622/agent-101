# Chapter 07 — Errors, Refusals, and Foot-Guns 🐢

> **A tool that crashes is a bug. A tool that returns its error as a string is graceful degradation. The agent loop must NEVER raise on a tool error.**

## 🐢 GuiGui says

Real tools fail constantly. Networks blip. Files vanish. Permissions get denied. The model hallucinates tool names. Your loop has to survive all of it without losing the conversation you've already paid tokens for. **The rule: tool errors flow as content, never as exceptions.**

## The idea

Four classes of failure your loop will see in production:

| Class | Example | What to do |
|---|---|---|
| Tool raised | `FileNotFoundError`, timeout, division by zero | Catch, return error string, set `is_error: true` |
| Unknown tool name | Model hallucinates a tool that doesn't exist | Return `"unknown tool: X"`, `is_error: true` |
| Wrong arguments | Missing required field, wrong type | Same as raise — return the validation error |
| Wrong stop_reason | `refusal`, `max_tokens` | Don't hide — surface to user (see [ch03](ch03_stop_reasons.md)) |

Errors flow back as `tool_result` content. Claude reads them, apologizes, tries something else. The conversation continues.

## What flows on the wire when a tool errors

```
TURN 1 — claude calls a tool that's about to fail
─────────────────────────────────────────────────────────────
YOU send:
  messages = [{"role": "user", "content": "what's the weather in Atlantis?"}]

API replies:
  content = [
    {"type": "tool_use", "id": "toolu_01...", "name": "weather",
     "input": {"city": "Atlantis"}}
  ]
  stop_reason = "tool_use"

TURN 2 — your tool raises; you return the error AS CONTENT
─────────────────────────────────────────────────────────────
your code:
  try:    out = weather("Atlantis")
  except: out = "unknown city: Atlantis. known: ['SF', 'NYC', 'Tokyo']"
  is_error = True

YOU send:
  messages.append({"role": "user", "content": [
    {"type": "tool_result",
     "tool_use_id": "toolu_01...",
     "content":     "unknown city: Atlantis. known: ['SF', 'NYC', 'Tokyo']",
     "is_error":    True}                    ← the magic flag
  ]})

API replies:
  content = [{"type": "text",
              "text": "Atlantis isn't in the database. Want SF or NYC instead?"}]
  stop_reason = "end_turn"
```

**The loop didn't crash.** Claude read the error, recovered gracefully. That's the whole pattern.

## Show me the code

```python
def dispatch(name, args) -> tuple[str, bool]:
    """Returns (content, is_error). NEVER raises."""
    try:
        if name not in HANDLERS:
            return f"unknown tool: {name}", True
        return HANDLERS[name](**args), False
    except Exception as e:
        return f"{type(e).__name__}: {e}", True

# inside the loop, when stop_reason == "tool_use":
results = []
for b in r.content:
    if b.type == "tool_use":
        content, is_err = dispatch(b.name, b.input)
        results.append({"type": "tool_result", "tool_use_id": b.id,
                        "content": content, "is_error": is_err})
msgs.append({"role": "user", "content": results})
```

Three rules baked into this code:
- `try/except` wraps every tool call — exceptions become strings.
- Unknown tool names return content, not raise.
- `is_error: true` is the *signal* — without it, claude treats the error string as a successful return.

## The 4 stop_reasons that need their own handling

Tool errors are one failure class. The others come from `stop_reason`:

```python
if r.stop_reason == "refusal":
    raise Refused(r)                              # surface; don't bury

if r.stop_reason == "max_tokens":
    raise Truncated(r)                            # YOUR cap was too low

if r.stop_reason == "model_context_window_exceeded":
    raise ContextOverflow(r)                      # MODEL's window full — compact

if r.stop_reason == "pause_turn":
    continue                                      # server tool needs more time
```

See [ch03](ch03_stop_reasons.md) for the full taxonomy.

## ⚠️ Watch out for

**The infinite-error loop.** Claude calls a buggy tool 50 times because the error said *"please try again."* Cause: the error string is a *suggestion* the model follows literally. **Fix:** include the retry count in the error after attempt 2 — `"this is the 3rd timeout. Stop retrying. Try a different approach."`.

**Hidden refusals.** Catching `stop_reason == "refusal"` and silently returning empty text means your user thinks the agent is broken. **Always surface refusals to the human** — they need to see what claude declined to do.

**Catching too broad.** `except Exception` is fine for tool dispatch, but DON'T wrap the entire loop in `except Exception`. Network errors, API errors, and KeyboardInterrupt all need different handling. See `agent.py` for the production pattern.

## ✅ Summary

- Never let a tool exception kill the agent loop. **Errors are content.**
- Set `is_error: true` so claude knows it didn't work.
- Refusals surface to the human — never hide.
- Cap retries with explicit messaging — don't let claude infinite-loop on the same error.

## 📝 Homework

```bash
python -m chapters.ch07_errors
```

1. **Trigger each class.** Run with prompts that cause: (a) tool exception (`weather("Atlantis")`), (b) unknown-tool hallucination, (c) max_tokens truncation. Watch the recovery in each.
2. **The infinite loop.** Write a tool that always returns `"transient error, please retry"` (no retry count). Watch claude loop until you Ctrl-C. **This is the failure mode the homework is teaching you to recognize.**
3. **Real recovery.** Add a `weather` tool that raises on unknown cities but suggests known ones in the error. Ask "what's the weather in Atlantis?" Verify claude pivots to a known city.

## 📚 References

- [Anthropic — Tool errors](https://docs.anthropic.com/en/docs/build-with-claude/tool-use#handling-tool-use-and-tool-result-content-blocks) — the `is_error: true` field
- [Anthropic — Handling stop_reason](https://docs.anthropic.com/en/api/handling-stop-reasons) — refusal, max_tokens, pause_turn handling
- [AWS Builders' Library — Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — patterns that apply to agent retry logic
- [Marc Brooker — Reliable software with retries](https://brooker.co.za/blog/2015/03/21/backoff.html) — the exponential backoff math behind `agent.py`'s `with_retries()`

## 🚀 Next

[Chapter 08 — System prompts](ch08_system_prompts.md): what goes in `system` vs `messages`?
