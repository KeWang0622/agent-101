# Chapter 02 — The Messages Array IS the Memory

> **The most common confusion when starting with LLM APIs:
> "why does the model forget what I just told it?"**
> **Answer: because the API is stateless. There is no memory inside Claude.
> The `messages` array — the list you maintain in your code — IS the memory.**

## The hook

Open the Anthropic Discord or any LLM Stack Overflow tag and search for *"why does Claude forget?"*. You'll find a hundred posts, all asking variants of the same question, all writing code that calls the API once per turn with a fresh prompt and wondering why nothing carries over. The mental model that does this damage is "Claude has memory like ChatGPT.com." Claude's web app does. Claude's API does not. There is no `conversation_id`. There is no session. Every API call is a function from `(messages, tools, system) → next_message`. If you want continuity, you carry the array yourself.

This is the conceptual leap of building agents from raw APIs. Once you internalize it, every other concept in this repo is a corollary.

## The wrong version

```python
# the dead-end pattern
def chat(prompt: str) -> str:
    r = client.messages.create(
        model="claude-sonnet-4-5", max_tokens=1024,
        messages=[{"role": "user", "content": prompt}])
    return r.content[0].text

chat("my name is ke")
chat("what's my name?")    # → "I don't know your name."
```

Each call ships ONE message. The model has no idea you just told it your name two seconds ago. It doesn't even know the previous call existed.

## The right version

```python
messages: list[dict] = []
def chat(prompt: str) -> str:
    messages.append({"role": "user", "content": prompt})
    r = client.messages.create(
        model="claude-sonnet-4-5", max_tokens=1024, messages=messages)
    messages.append({"role": "assistant", "content": r.content})
    return "".join(b.text for b in r.content if b.type == "text")

chat("my name is ke")        # ↑ messages.len = 2
chat("what's my name?")      # ↑ messages.len = 4 ; "Your name is Ke."
```

Two changes:

1. `messages` is module-level (or session-scoped, or whatever you want) — *you* hold it.
2. After each call you append the assistant's reply back into the array. Note the `r.content` — we pass the *whole* content list back, including any tool_use blocks the model produced. The API expects the assistant turn to be reflected back exactly.

The array now grows by **2 per turn**. After N turns it has 2N messages. Every API call ships all of them.

## The mental model

```
turn 1                turn 2                turn 3
─────────             ─────────             ─────────
[                     [                     [
  user:  "hi"           user:  "hi"           user:  "hi"
                        asst:  "hello"        asst:  "hello"
]                       user:  "name?"        user:  "name?"
                      ]                       asst:  "Claude"
                                              user:  "thanks"
                                            ]

len = 1               len = 3               len = 5
```

Every call: send the **entire** list. The model has no memory of its own. The array IS the memory. It grows by exactly 2 per turn. Forever — until ch10 (compaction) gives you the surgery for when "forever" becomes "expensive."

## What could go wrong

**The role-alternation violation.** Symptom: API returns `400 messages: roles must alternate between "user" and "assistant"`. Cause: you appended two `user` messages in a row (forgot to append the assistant reply between them) or two `assistant` messages.

Fix: invariant — after every API call that returns successfully, you immediately append the assistant message; after every user input, you immediately append the user message. If a call fails, do NOT append the user message — `messages` stays in a valid state for retry.

This is the failure mode `agent.py`'s `Session.truncate_orphan_user()` recovers from on `--resume`: a previous run crashed after appending the user message but before getting the assistant reply. On resume, that orphan user gets dropped.

## Try this

```bash
python -m chapters.ch02_messages_array
```

1. Open a multi-turn chat. Tell the agent your favorite color. Three turns later, ask "what's my favorite color?" — confirm it remembers.
2. Add `print(json.dumps(messages, default=str, indent=2))` after the second turn. Read the actual array. See user/assistant alternation.
3. Comment out `messages.append({"role": "assistant", ...})`. Watch the next turn break with the role-alternation 400 error.

## When NOT to use this

For one-shot translations, classifications, or extractions, you don't need the array — call the API once with the prompt and return. The array adds value when *the next turn depends on the previous turn*.

## Where this shows up in agent.py

The whole repo is built on this primitive. Specifically: `Session` (lines 339–406) wraps a `messages` array with JSONL persistence, `compact_messages` (lines 416–448) operates on it, and `agent_turn` (lines 487–540) reads-and-writes it on every iteration. The array is the load-bearing data structure of the entire harness.

## Going deeper

- [Anthropic — Messages API](https://docs.anthropic.com/en/api/messages) — the role/content shape
- [OpenAI — managing conversation state](https://platform.openai.com/docs/guides/responses) — same idea, different name
- [Why Claude forgets](https://claudelab.net/en/articles/claude-ai/claude-forgets-context-conversation-memory-fix) — typical reader's first frustration
