# Chapter 04 — Your First Tool 🐢

> **The model can't run code. You can. A tool is the contract between them.**

## 🐢 GuiGui says

The model is a *suggester*; you are an *interpreter*. When Claude says "I'll check that for you" with a `tool_use` block, that's a *request* — your code runs the actual command and sends the result back. **The separation between the model and tool execution is the entire architectural insight of an agent.**

## What's a "tool", really?

A tool is **two things**, paired together:

1. **A Python function** that does the work. Same as any function you'd write — you can import it, test it, profile it.
2. **A JSON Schema description** that tells Claude *when* to call it and *what* to pass.

You write the function. You write the description. Claude reads the description, decides to use it, and emits a *request* to call it. **Your code runs the function.** Then you send the result back.

The model never executes any code. It just asks you to.

### The two things, side by side

```python
# 1. THE FUNCTION — plain Python.
def calculator(expression: str) -> str:
    return str(eval(expression))           # toy: never use eval in production

# 2. THE DESCRIPTION — a dict the model sees. claude uses this to decide:
#    "should I call this tool? what should I pass it?"
TOOL_SCHEMA = {
    "name": "calculator",                  # function-call name (must match)
    "description": "Evaluate a Python math expression. Use for any arithmetic.",
    "input_schema": {                      # JSON Schema for the args
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Python-syntax expression like '17 * 23'"
            }
        },
        "required": ["expression"],
    },
}
```

The `description` strings are **load-bearing**. Claude reads `"Use for any arithmetic"` and decides "yes, this is what I need." A bad description = your tool sits unused.

## What flows on the wire

```
TURN 1 — user asks something
─────────────────────────────────────────────────────────────
YOU send:
  messages = [{"role": "user", "content": "what is 17 * 23?"}]
  tools    = [TOOL_SCHEMA]

API replies:
  content = [
    {"type": "text", "text": "I'll calculate that for you."},
    {"type": "tool_use",
     "id":   "toolu_01ABC...",                  ← unique ID for this call
     "name": "calculator",                       ← matches TOOL_SCHEMA["name"]
     "input": {"expression": "17 * 23"}}        ← claude's chosen args
  ]
  stop_reason = "tool_use"                      ← signals "I need you to run this"

TURN 2 — you run the tool, send the result back
─────────────────────────────────────────────────────────────
YOU send (note: append BOTH messages, in order):
  messages = [
    {"role": "user",      "content": "what is 17 * 23?"},
    {"role": "assistant", "content": [...the content blocks above...]},
    {"role": "user",      "content": [
      {"type": "tool_result",
       "tool_use_id": "toolu_01ABC...",         ← MUST match the tool_use id
       "content":     "391"}                     ← what your function returned
    ]}
  ]

API replies:
  content     = [{"type": "text", "text": "17 × 23 = 391."}]
  stop_reason = "end_turn"                       ← done
```

**Two API calls. One round-trip per tool.** The next chapter ([ch05](ch05_the_loop.md)) wraps this in `while True` so claude can call any number of tools.

## The minimum agent code

```python
TOOLS = [TOOL_SCHEMA]
HANDLERS = {"calculator": calculator}                          # name → function

msgs = [{"role": "user", "content": "what is 1234 * 5678?"}]

# round 1: claude asks for the tool
r = client.messages.create(model=M, tools=TOOLS, messages=msgs, max_tokens=1024)
msgs.append({"role": "assistant", "content": r.content})       # append FIRST

# run every tool_use block in the reply
results = []
for b in r.content:
    if b.type == "tool_use":
        out = HANDLERS[b.name](**b.input)                      # call your function
        results.append({"type": "tool_result",
                        "tool_use_id": b.id, "content": out})

# round 2: send results back, get the final answer
msgs.append({"role": "user", "content": results})
r2 = client.messages.create(model=M, tools=TOOLS, messages=msgs, max_tokens=1024)
print("".join(b.text for b in r2.content if b.type == "text"))
```

That's the entire ch04. Two API calls, one tool, ~15 lines.

## The five things you must do correctly

1. **Iterate `r.content`, don't index.** A single assistant message can contain text AND tool_use blocks at once. `r.content` is always a list — even when it has one block.

   ```python
   for b in r.content:
       if b.type == "tool_use":
           # this is a tool call to handle
       elif b.type == "text":
           # this is text claude said before/with the call
   ```

2. **Append the assistant's `r.content` to messages BEFORE the tool_result.** The order on the wire must be: `user → assistant(tool_use) → user(tool_result)`. Skip the assistant turn and the API rejects.

3. **Match `tool_use_id` exactly.** Copy it from the block — never construct it yourself. Mismatch = `400 tool_use ids did not have corresponding tool_result blocks`.

4. **`tool_result.content` is a string** (or a list of content blocks for multi-modal results). Your function should return a string. If it returned a dict, `json.dumps()` it.

5. **Tool errors are content, not exceptions.** If your function raises, return `"ERROR: ..."` as the content with `is_error: true`. Never let an exception kill the loop. (Full chapter on this: [ch07](ch07_errors.md).)

## ⚠️ Watch out for

**The orphan tool_use.** `400 tool_use ids did not have corresponding tool_result blocks`. Every `tool_use` in an assistant message MUST be followed by a user message with a matching `tool_result`. No interleaving.

**The text-before-tool_result trap.** `tool_result` blocks must come FIRST in the user message's content array. A "Here are the results:" preamble before a `tool_result` block returns 400. If you want narration, put it AFTER the tool_results.

**Bad descriptions = ignored tools.** If your `description` is vague (`"Helps with math"`) Claude won't pick it. Specific descriptions (`"Evaluate a Python math expression. Use for any arithmetic."`) get picked reliably. **You shape the model's behavior by writing descriptions.**

## ✅ Summary

- A tool is a Python function PLUS a JSON-Schema description.
- The protocol: `tool_use` → run locally → `tool_result` → final answer. **Two API calls.**
- `tool_use` and matching `tool_result` must be adjacent in messages.
- Tool descriptions are load-bearing — claude picks tools based on what they say.

## 📝 Homework

```bash
python -m chapters.ch04_one_tool "what is 1234 * 5678?"
```

1. **See the trace.** Add `print(r.content)` after the first API call. Read the text + tool_use blocks side by side.
2. **Add a second tool.** Write `weather(city)` returning hard-coded data. Update TOOLS + HANDLERS. Ask claude a weather question.
3. **Force a tool.** Set `tool_choice={"type": "tool", "name": "calculator"}`. Watch claude be FORCED to call it even when it doesn't want to.
4. **Break the description.** Change `"Evaluate a Python math expression. Use for any arithmetic."` → `"Helps with stuff."`. Re-run. See if claude still picks it.

## 📚 References

- [Anthropic — Tool use overview](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — official protocol
- [Anthropic — Handling tool calls](https://docs.anthropic.com/en/agents-and-tools/tool-use/handle-tool-calls) — every constraint, including "tool_result first in content array"
- [Anthropic — Tool choice](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/tool-choice) — `auto`, `any`, force a specific tool
- [JSON Schema](https://json-schema.org/) — the spec for `input_schema`
- [Schick et al. — Toolformer (2023)](https://arxiv.org/abs/2302.04761) — the foundational paper on teaching LLMs to use tools

## 🚀 Next

[Chapter 05 — THE LOOP](ch05_the_loop.md): formalize this into 6 lines that are every agent on Earth.
