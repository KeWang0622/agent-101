# Chapter 16 — Streaming `tool_use` (The Hard Chapter) 🐢

> **Text deltas you render. tool_use deltas you ACCUMULATE. Don't mix them up.**

## 🐢 GuiGui says

This is the most-asked, most-bug-reported topic on the Anthropic SDK forum. You CAN'T `json.parse` a partial fragment. `'{"expr'` is not valid JSON. Buffer the fragments. Parse only on `content_block_stop`.

## The rule

| Block type | Delta name | Action |
|---|---|---|
| `text` | `text_delta` | Render immediately |
| `tool_use` | `input_json_delta` | **Accumulate. Parse on stop.** |

## Show me the code

```python
buffers = {}                              # index -> partial JSON string

for event, data in stream(...):
    if event == "content_block_start":
        if data["content_block"]["type"] == "tool_use":
            buffers[data["index"]] = ""

    elif event == "content_block_delta":
        d = data["delta"]
        if d["type"] == "text_delta":
            print(d["text"], end="", flush=True)
        elif d["type"] == "input_json_delta":
            buffers[data["index"]] += d["partial_json"]   # accumulate

    elif event == "content_block_stop":
        idx = data["index"]
        if idx in buffers:
            args = json.loads(buffers[idx])               # NOW parse
            dispatch(name, args)
```

## ⚠️ Watch out for

**The truncated tool args.** `JSONDecodeError` at the END of streaming. Buffer reads `'{"path": "/etc/host'` (no closing brace). Cause: `max_tokens` cut the response mid-args. Fix: check `stop_reason == "max_tokens"` BEFORE parsing.

## ✅ Summary

- `text_delta` → render now.
- `input_json_delta` → accumulate, parse on stop.
- Always check stop_reason before parsing the buffer.

## 📝 Homework

```bash
python -m chapters.ch16_streaming_tools "what's 999 * 999, then a joke about it?"
```

1. Watch the trace. Text deltas render character-by-character; tool_use shows up only after stop.
2. Force a truncation: `max_tokens=20`. Catch the JSON error. Surface a clear message.
3. Implement a "live tool args" UI that shows the buffer contents as it grows (just for debug).

## 🚀 Next

[Chapter 17 — Multi-provider](ch17_multi_provider.md): same loop, three wires.
