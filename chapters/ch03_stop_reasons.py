"""
chapter 03 — stop reasons (the seven ways a reply can end)

before tools, learn the EXIT CONDITIONS. an agent loop is `while True`, and
the way out is `stop_reason`. there are seven values you'll see, and your
loop must handle each correctly. most beginners write
`while stop_reason == "tool_use"` and get bitten when `max_tokens` truncates
a reply mid-thought.

the seven stop_reasons:
  end_turn                         — the model finished naturally. usually loop exit.
  tool_use                         — the reply ended with a tool_use block. you
                                     must run the tool and send tool_result.
  max_tokens                       — the reply was cut off (your `max_tokens` cap).
                                     either accept truncation, retry, or ask to
                                     continue ("please continue from where you
                                     stopped").
  stop_sequence                    — hit a string in your `stop_sequences` list.
  refusal                          — the model declined. surface to the user.
  pause_turn                       — server-side tool needs more time. retry
                                     with the same messages to continue.
  model_context_window_exceeded    — added with Sonnet 4.5: the request hit the
                                     model's context window limit (different
                                     from `max_tokens`, which is YOUR cap).
                                     retry with smaller messages or a model
                                     with a larger window.

what you'll learn:
  - which stop_reasons exit the loop and which continue it
  - the truncation foot-gun: max_tokens leaves you mid-JSON if streaming tools
  - the canonical control flow for an agent

we trigger end_turn / max_tokens / stop_sequence on purpose so you see them
with your own eyes. tool_use is triggered in ch04. refusal / pause_turn /
model_context_window_exceeded are operationally rare but you must handle them.

run:
  python -m chapters.ch03_stop_reasons

next: ch04 — your first tool. now the loop has a reason to exist.
"""

import os
import sys

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-6"


def show(label: str, **kwargs):
    print(f"\n=== {label} ===")
    r = client.messages.create(model=MODEL, **kwargs)
    print(f"stop_reason: {r.stop_reason!r}")
    print(f"output_tokens: {r.usage.output_tokens}")
    text = "".join(b.text for b in r.content if b.type == "text")
    print(f"text: {text[:140]}{'...' if len(text) > 140 else ''}")


def main():
    # 1. end_turn — the normal case.
    show("end_turn (normal)",
         max_tokens=200,
         messages=[{"role": "user", "content": "say hi in one short sentence"}])

    # 2. max_tokens — set max_tokens absurdly low and watch truncate mid-word.
    show("max_tokens (truncated)",
         max_tokens=8,
         messages=[{"role": "user", "content": "tell me a story about a fox"}])

    # 3. stop_sequence — provide a literal string that ends generation early.
    show("stop_sequence",
         max_tokens=200,
         stop_sequences=["END"],
         messages=[{"role": "user", "content":
                    "list 1, 2, 3, then write the word END."}])

    # 4. tool_use is in ch04 — we declare a tool there.
    print("\n=== tool_use (deferred) ===")
    print("see ch04 — we'll trigger this once we declare a tool.")

    # 5. refusal / 6. pause_turn / 7. model_context_window_exceeded
    # operationally rare. your loop must still handle them. canonical control
    # flow handles all 7:
    print("""
canonical loop (handles every stop_reason exhaustively):

  while True:
      r = client.messages.create(model=..., messages=msgs, tools=TOOLS)
      msgs.append({"role": "assistant", "content": r.content})

      if r.stop_reason == "end_turn":      return r            # done
      if r.stop_reason == "stop_sequence": return r            # done
      if r.stop_reason == "refusal":       raise Refused(r)    # surface it
      if r.stop_reason == "max_tokens":    raise Truncated(r)  # hard fail
      if r.stop_reason == "model_context_window_exceeded":
          raise ContextOverflow(r)                             # compact + retry
      if r.stop_reason == "pause_turn":    continue            # server tool
      if r.stop_reason == "tool_use":
          msgs.append({"role": "user", "content": run_tools(r.content)})
          continue
      raise UnknownStopReason(r.stop_reason)                   # forward-compat
""")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    main()
