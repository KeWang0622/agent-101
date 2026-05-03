# Chapter 01 — The Raw API Call 🐢

> **An "agent" is a `while` loop wrapped around an HTTP request. Before the loop, see what one request actually looks like.**

## 🐢 GuiGui says

The Anthropic SDK is 4,000 lines wrapping ONE HTTP POST. We're skipping the SDK for this one chapter so you see the request and response with your own eyes. Mental model: Claude is not an *object that holds state*. Claude is `urllib.urlopen("api.anthropic.com").read()`.

## The idea

The Messages API is one POST. JSON in, JSON out. Seven response fields: `id`, `type`, `role`, `model`, `content`, `stop_reason`, `usage`.

The most important: **`content` is a LIST of blocks**, not a string. Even when it has one block.

## Show me the code

```python
import json, os, urllib.request

body = json.dumps({
    "model": "claude-sonnet-4-5", "max_tokens": 1024,
    "messages": [{"role": "user", "content": "what is an agent?"}],
}).encode()

req = urllib.request.Request("https://api.anthropic.com/v1/messages",
    data=body, method="POST",
    headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
             "anthropic-version": "2023-06-01",
             "content-type": "application/json"})

with urllib.request.urlopen(req) as r:
    response = json.loads(r.read())

text = "".join(b["text"] for b in response["content"] if b["type"] == "text")
```

That last line is the canonical pattern: iterate `content`, filter type, join. Robust to multi-block replies.

## ⚠️ Watch out for

**The string-not-list assumption.** `response["content"][:50]` doesn't work — `content` is a list of blocks, not a string. Even with one block.

## ✅ Summary

- One POST to `/v1/messages`. JSON body in, JSON response out.
- `content` is a LIST of blocks. Always iterate, never index as string.
- Production: use the SDK. This chapter, deliberately, doesn't.

## 📝 Homework

```bash
python -m chapters.ch01_raw_call "explain agents in one sentence"
```

1. Read the full JSON response. Find `usage.input_tokens` and `usage.output_tokens`.
2. Compute the cost: `input * $3/1M + output * $15/1M`. That's what one call costs you.
3. Add `"system": "Reply only in haiku."` to the request body. Re-run.

## 📚 References

- [Anthropic — Messages API reference](https://docs.anthropic.com/en/api/messages) — every field, every shape
- [Anthropic — API versioning](https://docs.anthropic.com/en/api/versioning) — why we send `anthropic-version: 2023-06-01`
- [anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python) — what we're NOT using in this chapter
- [Hugging Face — Inference Providers](https://huggingface.co/docs/inference-providers) — same wire format works against many backends

## 🚀 Next

[Chapter 02 — Messages array](ch02_messages_array.md): the API has no memory. Why does it remember the last turn?
