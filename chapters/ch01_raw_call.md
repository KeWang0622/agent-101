# Chapter 01 — The Raw API Call

> **An "agent" is a while-loop wrapped around an HTTP request. Before the loop,
> see what one request actually looks like — no SDK, no framework, just
> `urllib.urlopen`.**

## The hook

If you've used the Anthropic SDK, you've typed `client.messages.create(...)` and treated it as one operation. It isn't. It's a single HTTP POST with a JSON body. The SDK is 4,000 lines of Python around that one POST. Strip every layer and you find the same thing the SDK finds: a request object, a response object, a JSON parse. We're going to look at it once with no abstractions so you understand exactly what the SDK is doing for you when you let it.

## The wrong version

Most "build an agent" tutorials open with `from anthropic import Anthropic` — and the reader builds a mental model where Claude is an *object* that *holds state*. They get to chapter 3 and discover the API is stateless and they have to maintain `messages` themselves, and the whole mental model collapses. We're going to avoid that by skipping the SDK for one chapter.

## The right version

```python
import json, os, urllib.request
body = json.dumps({
    "model": "claude-sonnet-4-5",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "what is an agent?"}],
}).encode()
req = urllib.request.Request("https://api.anthropic.com/v1/messages",
    data=body, method="POST",
    headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
             "anthropic-version": "2023-06-01",
             "content-type": "application/json"})
with urllib.request.urlopen(req) as r:
    response = json.loads(r.read())
```

That's it. No SDK. The response is a JSON dict with seven fields: `id`, `type`, `role`, `model`, `content`, `stop_reason`, `usage`. The SDK wraps these in a typed object (`Message` with `Message.content[0].text`); the wire format is a plain dict.

The `content` field is the most important one. It's a **list** of "content blocks" — for plain text replies, one block of `{"type": "text", "text": "..."}`. We'll see `tool_use` and `thinking` blocks in later chapters. Always treat content as a list.

## What could go wrong

**The string-not-list assumption.** Symptom: you write `response["content"][:50]` to print the first 50 characters and get a KeyError or a list slice you didn't want. Cause: `content` is a list of blocks, not a string. Even when it has one block.

Fix: `text = "".join(b["text"] for b in response["content"] if b["type"] == "text")`. This is the canonical pattern; it's robust to multi-block replies (text + tool_use mixed). The SDK does this for you when you access `Message.content[0].text` — but only because there's one block. Two blocks and that line breaks too.

## Try this

```bash
python -m chapters.ch01_raw_call "what is an agent?"
```

1. Read the full JSON response printed by the script. Find `usage.input_tokens` and `usage.output_tokens`. Multiply by Sonnet 4.5 pricing — that's what the call cost.
2. Change `max_tokens` to 5. Rerun. Watch the response truncate mid-sentence. Look at `stop_reason`. Now you've seen `max_tokens` (we'll formalize in ch03).
3. Add a `system` field to the request body: `"system": "Reply only in haiku."`. Rerun. The response should now be a haiku.

## When NOT to use this

Production code — use the SDK. The SDK handles connection pooling, retries, streaming, type validation, and protocol versioning. We're using `urllib` here once, deliberately, to remove all of those affordances and see the bare HTTP exchange.

## Where this shows up in agent.py

`agent.py` uses the Anthropic SDK throughout. The thing happening in `client.messages.stream(...)` is the same thing happening in this chapter, with one extra header (`stream: true`) and SSE chunks instead of one JSON response. Everything else is identical.

## Going deeper

- [Messages API reference](https://docs.anthropic.com/en/api/messages) — the canonical spec
- [Anthropic Python SDK source](https://github.com/anthropics/anthropic-sdk-python) — what we're NOT using
- [Hugging Face — Inference Providers](https://huggingface.co/docs/inference-providers) — the same wire format works against many backends
