# Chapter 02 — The Messages Array IS the Memory 🐢

> **The most common confusion when starting with LLM APIs: "why does the model forget what I just told it?" Answer: because the API is stateless. The `messages` array — the list YOU maintain in your code — IS the memory.**

## 🐢 GuiGui says

Claude.ai (the website) has memory. The API does NOT. There is no `conversation_id`, no session token, no hidden state. Every API call is `(messages, tools, system) → next_message`. If you want continuity, you carry the list yourself.

This is *the* conceptual leap of building agents from raw APIs. Once you internalize it, every other concept becomes obvious.

## The idea

```
turn 1                    turn 2                    turn 3
[                         [                         [
  user: "hi"                user: "hi"                user: "hi"
                            asst: "hello"             asst: "hello"
]                           user: "name?"             user: "name?"
                          ]                           asst: "Claude"
                                                      user: "thanks"
                                                    ]
len = 1                   len = 3                   len = 5
```

Every call: send the **entire** list. The array grows by 2 per turn. Forever (until [ch10](ch10_compaction.md)).

## Show me the code

```python
messages = []                                       # YOU hold the state

while True:
    user_input = input("you> ")
    messages.append({"role": "user", "content": user_input})

    r = client.messages.create(model=M, max_tokens=1024, messages=messages)
    messages.append({"role": "assistant", "content": r.content})

    print("claude>", "".join(b.text for b in r.content if b.type == "text"))
```

## ⚠️ Watch out for

**The role-alternation violation.** `400 messages: roles must alternate`. Cause: you appended two `user` messages in a row. Fix: invariant — after every successful API call, immediately append the assistant; after every user input, immediately append user.

## ✅ Summary

- The API is stateless; the array is the memory.
- The array grows by 2 per turn.
- Roles must strictly alternate user/assistant.

## 📝 Homework

```bash
python -m chapters.ch02_messages_array
```

1. Multi-turn chat: tell it your favorite color. Two turns later, ask "what's my favorite color?". Confirm it remembers.
2. After turn 3, `print(json.dumps(messages, default=str, indent=2))`. Read the array.
3. Force the role-alternation 400 by appending two user messages in a row. See the error.

## 📚 References

- [Anthropic — Messages API: roles](https://docs.anthropic.com/en/api/messages#roles) — the alternation rule, formalized
- [OpenAI — Conversation state](https://platform.openai.com/docs/guides/responses) — same idea in a different vendor's vocabulary
- [Why Claude forgets — claudelab.net](https://claudelab.net/en/articles/claude-ai/claude-forgets-context-conversation-memory-fix) — the typical reader's first frustration

## 🚀 Next

[Chapter 03 — Stop reasons](ch03_stop_reasons.md): the loop is `while True`. The way OUT is `stop_reason`. There are seven values.
