# Chapter 00 — Welcome 🐢

> **A complete agent in 30 lines. Read it once. The next 17 chapters explain why it works.**

## 🐢 GuiGui says

Hi! Before any theory, let's see one work. This file is a `while True` loop, two tools, one Anthropic call per turn. **If you only have 5 minutes, this is the only file to read.**

## The idea

```
prompt → API call → if tool_use, run tool → loop → answer
```

That's the agent. Everything else (sessions, compaction, MCP, skills) is layers around this loop. By [chapter 5](ch05_the_loop.md) you'll write this from memory.

## Show me the code

```python
while True:
    r = client.messages.create(model=M, tools=TOOLS, messages=msgs, max_tokens=2048)
    msgs.append({"role": "assistant", "content": r.content})
    if r.stop_reason == "end_turn":
        return
    msgs.append({"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": b.id, "content": run(b.name, b.input)}
        for b in r.content if b.type == "tool_use"
    ]})
```

Six lines if you ignore formatting. That's literally it.

## ✅ Summary

- An agent is `while True` of API call → run tools → loop.
- The model is stateless; you carry state in `messages`.
- This whole repo is layers around these six lines.

## 📝 Homework

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python -m chapters.ch00_welcome "what is 17 * 23 in one sentence"
python -m chapters.ch00_welcome "list the python files in chapters/ and count them"
python -m chapters.ch00_welcome "find any TODO in this repo"
```

After all three: **what surprised you?** Open an issue if anything wasn't obvious.

## 🚀 Next

[Chapter 01 — Raw API call](ch01_raw_call.md): strip out the SDK and see the bytes.
