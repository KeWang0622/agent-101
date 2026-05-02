"""
chapter 04 — stop reasons (the four ways a reply can end)

before tools, learn the EXIT CONDITIONS. an agent loop is `while True`, and
the way out is `stop_reason`. there are four values you'll see, and your loop
must handle each correctly. most beginners write `while stop_reason == "tool_use"`
and get bitten when `max_tokens` truncates a reply mid-thought.

the four stop_reasons:
  end_turn           — the model finished naturally. usually loop exit.
  tool_use           — the reply ended with a tool_use block. you must run the
                       tool and send tool_result. this is the agent loop.
  max_tokens         — the reply was cut off. you need to either accept the
                       truncation, retry with more max_tokens, or ask to
                       continue ("please continue from where you stopped").
  stop_sequence      — the reply hit a `stop_sequences` string you provided.

what you'll learn:
  - which stop_reasons exit the loop and which continue it
  - the truncation foot-gun: max_tokens leaves you mid-JSON if streaming tools
  - the canonical control flow for an agent

we trigger each stop_reason on purpose so you see them with your own eyes.

run:
  python -m chapters.ch04_stop_reasons

next: ch05 — your first tool. now the loop has a reason to exist.
"""

import os
import sys

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-5"


def show(label: str, **kwargs):
    print(f"\n=== {label} ===")
    r = client.messages.create(model=MODEL, **kwargs)
    print(f"stop_reason: {r.stop_reason!r}")
    print(f"output_tokens: {r.usage.output_tokens}")
    text = "".join(b.text for b in r.content if b.type == "text")
    print(f"text: {text[:140]}{'...' if len(text) > 140 else ''}")


def main():
    # 1. end_turn — the normal case. claude finishes a sentence, says goodbye.
    show("end_turn (normal)",
         max_tokens=200,
         messages=[{"role": "user", "content": "say hi in one short sentence"}])

    # 2. max_tokens — set max_tokens absurdly low and watch the reply truncate
    #    mid-word. this is the silent killer of streaming tool_use. always
    #    check stop_reason before parsing the output.
    show("max_tokens (truncated)",
         max_tokens=8,
         messages=[{"role": "user", "content": "tell me a story about a fox"}])

    # 3. stop_sequence — provide a literal string that ends generation early.
    #    rarely useful for agents but worth seeing once.
    show("stop_sequence",
         max_tokens=200,
         stop_sequences=["END"],
         messages=[{"role": "user", "content":
                    "list 1, 2, 3, then write the word END."}])

    # 4. tool_use we'll trigger in chapter 5. mentioned here for completeness:
    #    when the model decides to call a tool, the reply ends with a
    #    tool_use block and stop_reason="tool_use". your job: run the tool
    #    and send tool_result.
    print("\n=== tool_use (deferred) ===")
    print("see ch05 — we'll trigger this once we declare a tool.")

    print("""
canonical loop:
  while True:
      r = client.messages.create(model=..., messages=msgs, tools=TOOLS)
      msgs.append({"role": "assistant", "content": r.content})

      if r.stop_reason == "end_turn":          break              # done
      if r.stop_reason == "max_tokens":        raise Truncated()  # hard fail
      if r.stop_reason == "stop_sequence":     break              # done
      if r.stop_reason == "tool_use":
          msgs.append({"role": "user",
                       "content": run_tools(r.content)})
          continue
      raise UnknownStopReason(r.stop_reason)
""")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    main()
