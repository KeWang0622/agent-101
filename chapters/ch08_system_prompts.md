# Chapter 08 — System Prompts 🐢

> **The system prompt is what the model IS. Messages are what it just DID. Tools are what it CAN do. Don't mix them up.**

## 🐢 GuiGui says

Beginners stuff instructions into the first user message. Works for one-shot. Fails for agents — instructions scroll off, prompt cache misses, persona drifts. Persistent instructions go in `system`.

## The idea

| Where | What goes here | Cacheable? |
|---|---|---|
| `system` | Persona, policies, AGENT.md | ✅ |
| `messages` | The conversation | ❌ |
| `tools` | Capabilities + JSON Schema | ✅ |

## Show me the code

```python
SYSTEM = "You are a careful coding agent. Read files before editing them."

# basic
r = client.messages.create(
    model=M, system=SYSTEM,
    messages=msgs, tools=TOOLS, max_tokens=1024,
)

# with caching (one extra wrapper, ~10× cheaper on input)
system_cached = [{"type": "text", "text": SYSTEM,
                  "cache_control": {"type": "ephemeral"}}]
```

That's the entire system-prompt API. `cache_control` is one wrapper away.

## ⚠️ Watch out for

**The persona drift.** Persona in the first user message gets compacted away by [ch10](ch10_compaction.md). Persona in `system` survives forever — compaction never touches it.

## ✅ Summary

- `system` is persistent identity. Use it.
- Wrap with `cache_control` for ~10× input cost reduction.
- `system` survives compaction; user messages don't.

## 📝 Homework

```bash
python -m chapters.ch08_system_prompts
```

1. Same question, three system prompts. Compare voices.
2. Wrap `system` with `cache_control`. Run twice. Check `cache_read_input_tokens`.
3. Find one place in `agent.py` where changing the system prompt would alter behavior.

## 📚 References

- [Anthropic — System prompts](https://docs.anthropic.com/en/docs/build-with-claude/system-prompts) — official guide
- [Anthropic — Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) — the canonical prompt techniques
- [Anthropic — `developer` role for OpenAI compatibility](https://platform.openai.com/docs/guides/text-generation) — note: OpenAI deprecated `system` in favor of `developer` (2026)

## 🚀 Next

[Chapter 08b — The dollar ticker](ch08b_observability.md): what does each turn actually cost?
