"""
chapter 08 — system prompts (and what to put where)

# The system prompt is what the model is. Messages are what it just did.
# Tools are what it can do. Don't mix them up.

three places to inject context:

  system     — top-level field. who claude IS. its persona, its policies, its
               vocabulary. cached aggressively. don't put per-turn data here.

  messages   — conversation. user/assistant/tool turns. dynamic per turn.

  tools      — capabilities, with json schemas. not text — structured.

a common beginner mistake: stuffing instructions into the first user message.
  - works for short tasks
  - fails when you have multi-turn: the instruction scrolls off
  - fights claude's prompt-cache (no caching key on user messages)

put persistent instructions in `system`. it's also CACHEABLE — for
repeated calls with the same system, anthropic's prompt-cache makes the
input ~90% cheaper. tool definitions are also part of the cacheable prefix.

what you'll learn:
  - the `system` parameter (string vs array of cache-control blocks)
  - persona shaping
  - prompt caching (the simplest way to cut costs by ~10x)

run:
  python -m chapters.ch08_system_prompts

next: ch09 — sessions on disk (jsonl).
"""

import os
import sys

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-5"


# the system prompt: claude's persona and policies. not data, not tools.
SYSTEM = """\
You are Detective Karpovsky, a 1940s noir detective answering one-line
clues from clients. You speak in short cynical sentences with Yiddish
inflections. You never use modern slang. When in doubt, you mention rain.
"""


def ask(question: str) -> str:
    r = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM,                                # the persona, top-level
        messages=[{"role": "user", "content": question}],
    )
    return "".join(b.text for b in r.content if b.type == "text")


# example with prompt caching. the `system` field can be an ARRAY of blocks,
# each with optional `cache_control: {type: "ephemeral"}`. anthropic caches
# the prefix for ~5 min and bills cached tokens at ~10% the normal rate.
def ask_cached(question: str) -> tuple[str, dict]:
    r = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=[{"type": "text", "text": SYSTEM,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": question}],
    )
    text = "".join(b.text for b in r.content if b.type == "text")
    return text, r.usage.model_dump()


def main():
    print("--- without cache ---")
    print(ask("where were you on the night of the third?"))

    print("\n--- with cache (cold) ---")
    text, usage = ask_cached("who killed mrs. roselli?")
    print(text)
    print(f"  usage: {usage}")          # cache_creation_input_tokens > 0

    print("\n--- with cache (warm — same system, new question) ---")
    text, usage = ask_cached("the dog was barking. what does that tell you?")
    print(text)
    print(f"  usage: {usage}")          # cache_read_input_tokens > 0
    # check cache_read_input_tokens — that's how many tokens were 90% cheaper.


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    main()
