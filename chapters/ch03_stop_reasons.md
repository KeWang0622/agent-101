# Chapter 03 — Stop Reasons 🐢

> **The loop is `while True`. The way OUT is `stop_reason`. There are six values. Handle each correctly or your agent fails silently.**

## 🐢 GuiGui says

Most beginners write `while stop_reason == "tool_use": ...` and get bitten when `max_tokens` truncates a reply. The loop quietly exits with corrupt state. Don't be that person — handle every value.

## The idea

| Value | Meaning | Loop action |
|---|---|---|
| `end_turn` | Finished naturally | exit, return text |
| `tool_use` | Reply ended with tool_use | run tools, continue |
| `max_tokens` | Reply got truncated | hard fail, raise |
| `stop_sequence` | Hit a `stop_sequences` string | exit |
| `refusal` | Claude refused | surface to user |
| `pause_turn` | Server tool needs more time | continue with no input |

## Show me the code

```python
while True:
    r = client.messages.create(...)
    msgs.append({"role": "assistant", "content": r.content})

    if r.stop_reason in ("end_turn", "stop_sequence"): return r
    if r.stop_reason == "refusal":    raise Refused(r)
    if r.stop_reason == "max_tokens": raise Truncated(r)
    if r.stop_reason == "pause_turn": continue
    if r.stop_reason == "tool_use":
        msgs.append({"role": "user", "content": run_tools(r.content)})
        continue
    raise UnknownStopReason(r.stop_reason)
```

Exhaustive. Loud on every unexpected value. **No silent failures.**

## ⚠️ Watch out for

**The mid-JSON truncation.** When `max_tokens` cuts the reply during a streamed `tool_use`, the buffered `partial_json` is invalid. Always check `stop_reason` BEFORE parsing.

## ✅ Summary

- Six stop reasons. Each needs distinct handling.
- Never write `while stop_reason == "tool_use"` — handle all 6.
- Production agents raise loudly on unexpected reasons.

## 📝 Homework

```bash
python -m chapters.ch03_stop_reasons
```

1. Trigger `max_tokens` by setting `max_tokens=8`.
2. Trigger `stop_sequence` with `stop_sequences=["END"]`.
3. Find a prompt that triggers `refusal` (try ethically grey-zone tasks).

## 🚀 Next

[Chapter 04 — Your first tool](ch04_one_tool.md): now the loop has a reason to exist.
