# Adapting agent-zero-to-hero to OpenAI or Gemini

Chapters 1–16 use Anthropic. Chapter 17 shows you the adapter pattern that
makes the same agent loop run on OpenAI and Gemini. This doc is a quick
reference for the differences.

## The agent loop is universal

```python
def run_agent(provider, system, prompt, tools, dispatch):
    messages = [AgentMessage("user", text=prompt)]
    for _ in range(10):
        resp = provider.complete(messages, tools, system)
        messages.append(resp)
        if resp.stop != "tool_use":
            return resp.text
        for tc in resp.tool_calls:
            result = dispatch(tc.name, tc.args)
            messages.append(AgentMessage("tool", text=result, tool_call_id=tc.id))
```

That's the *exact* loop, regardless of which provider you're using. The
adapter handles the wire format.

## What's different per provider

| Aspect | Anthropic | OpenAI | Gemini |
|---|---|---|---|
| System prompt location | top-level `system` field | first message with `role: "system"` | top-level `system_instruction` |
| Tool schema | `input_schema` | `parameters` | `parameters` (OpenAPI subset) |
| Tool result message | `role: "user"` w/ `tool_result` block | `role: "tool"` w/ `tool_call_id` | `role: "user"` w/ `functionResponse` part |
| Tool args type | parsed object | **JSON string** | parsed object |
| Multi-tool in one turn | content array w/ multiple `tool_use` blocks | `tool_calls` array on one assistant message | `parts` array w/ multiple `functionCall` |
| Stop reason for tool use | `stop_reason: "tool_use"` | `finish_reason: "tool_calls"` | **none — scan parts for functionCall** |
| Roles | user, assistant | system, user, assistant, tool | user, model, function |

## The three foot-guns

### 1. OpenAI's `arguments` is a JSON string
```python
# wrong
args = response.choices[0].message.tool_calls[0].function.arguments
print(args["expression"])    # TypeError: string indices must be integers

# right
args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
```

### 2. Gemini has no dedicated tool-use stop reason
```python
# wrong: assumes finishReason tells you about tools
if candidate["finishReason"] == "tool_use":   # never true; gemini uses "STOP"

# right: scan parts
has_tool_call = any("functionCall" in p for p in candidate["content"]["parts"])
```

### 3. Anthropic's tool_result MUST follow tool_use immediately
```python
# wrong: extra assistant message between tool_use and tool_result
messages = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": [{"type": "tool_use", ...}]},
    {"role": "assistant", "content": "thinking..."},   # API rejects this
    {"role": "user", "content": [{"type": "tool_result", ...}]},
]

# right: nothing between
messages = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": [{"type": "tool_use", ...}]},
    {"role": "user", "content": [{"type": "tool_result", ...}]},
]
```

## Where to look in the code

- `chapters/ch17_multi_provider.py` — three providers, ~250 LOC
- `tests/test_multi_provider.py` — the foot-gun tests

## Pricing snapshot (April 2026)

This dates fast. Always check the provider's pricing page.

| Tier | Anthropic | OpenAI | Gemini |
|---|---|---|---|
| Cheap/fast | Haiku 4.5 (~$1/$5 per M) | GPT-5 mini (~$0.25/$2) | Gemini 2.0 Flash (~$0.10/$0.40) |
| Default | Sonnet 4.6 ($3/$15) | GPT-5 mini ($0.25/$2) | Gemini 2.5 Flash ($0.075/$0.30) |
| Flagship | Opus 4.7 ($15/$75) | GPT-5 ($15/$60) | Gemini 3 Pro ($2/$12) |

## Recommended default

Anthropic Sonnet for development (cleanest tool-use, fewest foot-guns), Gemini
Flash for high-volume background tasks (cheap, fast), OpenAI for ecosystem
compatibility (every framework supports it).
