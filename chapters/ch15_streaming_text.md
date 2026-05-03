# Chapter 15 — Streaming Text via SSE 🐢

> **Streaming is engineering, not core. The agent loop works without it. But the UX is unrecognizable without it.**

## 🐢 GuiGui says

You've gotten this far without streaming. Why bother? Because the difference between Claude Code and "a script that prints when done" is tokens appearing one-at-a-time. It's the entire reason coding agents feel alive.

## The protocol

Add `"stream": true` to the request. The response becomes a sequence of Server-Sent Events:

```
event: message_start
event: content_block_start
event: content_block_delta    ← repeats with text fragments
event: content_block_stop
event: message_delta          ← final stop_reason here
event: message_stop
```

## Show me the code

```python
import json, urllib.request

def stream(prompt):
    body = json.dumps({"model": M, "stream": True, "max_tokens": 1024,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={...})
    with urllib.request.urlopen(req) as r:
        event = None
        for raw in r:
            line = raw.decode("utf-8").rstrip()
            if line.startswith("event: "):     event = line[7:]
            elif line.startswith("data: "):    yield event, json.loads(line[6:])

for event, data in stream("explain TCP"):
    if event == "content_block_delta" and data["delta"]["type"] == "text_delta":
        print(data["delta"]["text"], end="", flush=True)        # render NOW
```

15 lines including the parser. Text-only streaming is easy.

## ⚠️ Watch out for

**The buffered stdout.** Tokens appear all at once at the end. Cause: stdout buffering. Fix: `flush=True` on every `print`. Or `PYTHONUNBUFFERED=1`.

## ✅ Summary

- `stream: true` → response becomes Server-Sent Events.
- Text deltas are safe to render immediately.
- `tool_use` deltas are NOT — see [ch16](ch16_streaming_tools.md).

## 📝 Homework

```bash
python -m chapters.ch15_streaming_text "explain the agent loop in 3 sentences"
```

1. Watch tokens arrive at typing speed.
2. Compare wall-clock time vs non-streaming version. Same total time; different UX.
3. Add a typing-cursor character (`█`) that flickers between deltas.

## 📚 References

- [Anthropic — Streaming messages](https://docs.anthropic.com/en/api/messages-streaming) — every event type
- [SSE — Server-Sent Events spec (WHATWG)](https://html.spec.whatwg.org/multipage/server-sent-events.html) — the underlying protocol
- [Anthropic SDK — issue tracker (streaming)](https://github.com/anthropics/anthropic-sdk-typescript/issues?q=streaming) — community foot-guns
- [comparing streaming response structures across providers](https://medium.com/percolation-labs/comparing-the-streaming-response-structure-for-different-llm-apis-2b8645028b41) — Anthropic vs OpenAI vs Gemini SSE shapes

## 🚀 Next

[Chapter 16 — Streaming tool_use](ch16_streaming_tools.md): the hard chapter.
