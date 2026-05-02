# Chapter 04 — Your First Tool

> **The model can't run code. You can. A tool is the contract between them.**

## The hook

The first time someone "uses tools," the magic is so obvious it feels like a hidden API call. The model said "let me check that for you" and *did the thing* — read the file, ran the command, came back with an answer. The instinct is to assume Claude has shell access. It does not. Claude said `{"type":"tool_use","name":"bash","input":{"cmd":"ls"}}` to YOUR code, and YOUR code ran the shell command. The model is a *suggester*; you are an *interpreter*. That separation is the whole architectural insight.

## What you already know

From ch01: a request has `messages`. From ch02: that array is the memory. Now we add one more field: `tools`. When you include it, Claude is allowed to ask for tool calls in its response.

## The wrong version

```python
# the magic-thinking version
result = ask_claude("read /etc/hosts and tell me what's there")
# expects claude to actually read the file
```

Without a `tools` field, Claude can describe what it WOULD do. It cannot do it. The string `"read /etc/hosts"` in the response is a description, not an action.

## The right version

Three things:

1. **Declare the tool** with a JSON Schema:

```python
TOOLS = [{
    "name": "calculator",
    "description": "Evaluates a math expression. Use for any arithmetic.",
    "input_schema": {
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"],
    },
}]
```

2. **Watch for the tool_use response.** When Claude wants to call your tool, the response's `content` will include a `tool_use` block, and `stop_reason` will be `"tool_use"`:

```python
r = client.messages.create(model=M, tools=TOOLS, messages=msgs, max_tokens=1024)
msgs.append({"role": "assistant", "content": r.content})
# r.content is now: [text block, tool_use block, …]
# r.stop_reason == "tool_use"
```

3. **Run it locally and send the result back** as a `tool_result` block in a new user message:

```python
for b in r.content:
    if b.type == "tool_use":
        result = str(eval(b.input["expression"]))
        msgs.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": b.id, "content": result}
        ]})
```

Then call `client.messages.create` AGAIN with the now-larger messages array. Claude will see the tool result and produce the final answer. That's the round-trip: two API calls, one for the request, one for the answer-after-result.

In ch05 we'll wrap this in `while True` so the model can run any number of tools.

## What could go wrong

**The orphan tool_use.** Symptom: API rejects your next call with `"tool_use ids ... did not have corresponding tool_result blocks"`. Cause: the assistant message contained a `tool_use` block, but the next user message has no matching `tool_result` block (or a typo in the `tool_use_id`).

The rule: every `tool_use` in an assistant message MUST be followed by a user message containing a `tool_result` for that exact `tool_use_id`. No interleaving. No skipping. The pair is sacred. This is the most-cited foot-gun in the Anthropic forum.

Fix: copy the `tool_use_id` directly from the block — don't generate it yourself. And ALWAYS run all tool_use blocks from one assistant message before sending the next user turn.

## Try this

```bash
python -m chapters.ch04_one_tool "what is 17 * 23?"
```

1. Run it. Read the trace. Count the API calls (should be 2).
2. Print `r.content` after the first call. See the text block AND tool_use block coexist — the model often "talks while doing" ("I'll calculate that for you. [tool_use]").
3. Set `tool_choice={"type": "tool", "name": "calculator"}` on the request. Now Claude is FORCED to call calculator. Useful for forcing structured output (chapter on this in the wishlist).

## When NOT to use this

Tools cost an extra round-trip. For pure text tasks, just prompt and return — no tools. The break-even is ~2 round-trips: if your task usually needs the model to look something up, tools win on accuracy *and* often on cost (because the alternative is stuffing context).

## Where this shows up in agent.py

`agent.py`'s seven tools are declared the same way (lines 200–252). The dispatch — `DISPATCH = {"Read": tool_read, ...}` — is the same shape, just bigger. Every concept here scales linearly: 50 tools is 50 entries in `TOOLS` and 50 entries in `DISPATCH`. That's why this primitive scales to Cursor and Claude Code.

## Going deeper

- [Anthropic — Tool use docs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Anthropic — Tool choice](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/tool-choice) — `auto`, `any`, `tool`
- [JSON Schema](https://json-schema.org/) — the spec for `input_schema`
