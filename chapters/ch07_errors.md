# Chapter 07 — Errors, Refusals, and Foot-Guns 🐢

> **A tool that crashes is a bug. A tool that returns its error as a string is graceful degradation. The agent loop must NEVER raise on a tool error.**

## 🐢 GuiGui says

Real tools fail constantly. Networks blip. Files vanish. Models hallucinate tool names. Your loop has to survive all of it without losing the conversation. The rule is simple: **tool errors flow as content, never as exceptions.**

## The idea

| Failure | What to do |
|---|---|
| Tool raised | Return error string, set `is_error: true` |
| Unknown tool name | Return `"unknown tool: <name>"`, `is_error: true` |
| Wrong arguments | Catch, retry once, give up |
| Refusal stop_reason | Surface to user (don't hide) |

## Show me the code

```python
def dispatch(name, args) -> tuple[str, bool]:
    """Returns (content, is_error). Never raises."""
    try:
        if name not in HANDLERS:
            return f"unknown tool: {name}", True
        return HANDLERS[name](**args), False
    except Exception as e:
        return f"{type(e).__name__}: {e}", True

# in the loop:
content, is_err = dispatch(b.name, b.input)
results.append({"type": "tool_result", "tool_use_id": b.id,
                "content": content, "is_error": is_err})
```

The `is_error: true` flag tells claude "this didn't work." Without it, the error string looks like a successful return value.

## ⚠️ Watch out for

**The loop that won't quit.** Claude calls a buggy tool 50 times because the error said "please try again." Fix: include retry count in the error string after attempt 2.

## ✅ Summary

- Never let a tool exception kill the agent loop.
- Errors are content with `is_error: true`.
- Surface refusals; don't hide them.

## 📝 Homework

```bash
python -m chapters.ch07_errors
```

1. Add a 4th failure: network timeout in a tool. Show recovery.
2. Try a 1000-line file as input to a tool. Where does the limit hit?
3. **Adversarial test:** craft a prompt that makes claude infinite-loop on a buggy tool.

## 🚀 Next

[Chapter 08 — System prompts](ch08_system_prompts.md): what goes in `system` vs `messages`?
