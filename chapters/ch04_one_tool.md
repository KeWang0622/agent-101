# Chapter 04 — Your First Tool 🐢

> **The model can't run code. You can. A tool is the contract between them.**

## 🐢 GuiGui says

The model is a *suggester*; you are an *interpreter*. When Claude says "I'll check that for you" with a `tool_use` block, that's a request — your code runs the actual command and sends back the result. The separation between model and tool execution is the entire architectural insight of an agent.

## The idea

A tool is a triple: `{name, description, input_schema}` plus a function. When you include `tools=[...]` in a request, Claude is allowed to ask for tool calls. The protocol:

```
assistant turn:                     user turn (next):
  text "I'll calculate"               [tool_result(t1, "391")]
  tool_use(calc, "17*23", id=t1)
```

Two API calls. One round-trip. No magic.

## Show me the code

```python
TOOLS = [{
    "name": "calculator",
    "description": "Evaluate a math expression.",
    "input_schema": {
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"],
    },
}]

r = client.messages.create(model=M, tools=TOOLS, messages=msgs, max_tokens=1024)

if r.stop_reason == "tool_use":
    results = []
    for b in r.content:
        if b.type == "tool_use":
            answer = str(eval(b.input["expression"]))
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": answer})
    msgs.append({"role": "assistant", "content": r.content})
    msgs.append({"role": "user", "content": results})

    # call client.messages.create AGAIN with the now-larger messages array
```

## ⚠️ Watch out for

**The orphan tool_use.** `400 tool_use ids did not have corresponding tool_result blocks`. Every `tool_use` in an assistant message MUST be followed by a user message with a matching `tool_result`. No interleaving.

## ✅ Summary

- A tool is a JSON-Schema-described function the model can REQUEST.
- The protocol: tool_use → run locally → tool_result → final answer.
- `tool_use` and matching `tool_result` must be adjacent in messages.

## 📝 Homework

```bash
python -m chapters.ch04_one_tool "what is 1234 * 5678?"
```

1. Add a second tool: `weather(city)` that returns hard-coded data.
2. Set `tool_choice={"type": "tool", "name": "calculator"}`. Watch claude be FORCED to call it.
3. Print `r.content` after the first call. See text + tool_use blocks coexist.

## 🚀 Next

[Chapter 05 — THE LOOP](ch05_the_loop.md): formalize this into 6 lines that are every agent on Earth.
