"""
chapter 10 — compaction (the chapter that pays for itself)

# When your messages array gets too big, claude gets dumber AND more expensive.
# Compaction is one LLM call that summarizes old turns and lets you keep going.

every claude code user has seen "Compacting…" appear and wondered. this is the
chapter that demystifies it. it's ~80 lines.

  ┌───────────────────────────────────────────────────────────┐
  │  messages = [m1, m2, m3, m4, m5, m6, m7, m8, m9, m10]      │   stuffed
  └───────────────────────────────────────────────────────────┘
                            │
                  trigger: tokens > 70% of window
                            ▼
  ┌──────────┐  summarize via LLM   ┌──────────────────────────┐
  │  m1..m6  │ ───────────────────► │ "summary: did A, found B │  one user msg
  └──────────┘                      │  and C, decided D"       │
                                    └──────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  messages = [<summary>, m7, m8, m9, m10]                  │   recovered
  └──────────────────────────────────────────────────────────┘

design choices that matter:
  - WHEN to trigger: % of model context, not message count.
    rule of thumb: at 70% of input_window, perf drops; trigger at 60%.
  - WHAT to summarize: the OLDEST messages. recent ones are still load-bearing.
  - WHAT to preserve: file contents, tool outputs that are still active context.
    the summary should preserve identifiers (uuids, urls, paths) verbatim.
  - WHAT to drop: idle thinking, retried tool results, scrolled-out errors.
  - HOW to inject: as ONE user message at the start of the new array, with
    a clear preamble: "<summary of prior conversation>: ..."

what you'll learn:
  - token counting (count_tokens vs estimate_tokens)
  - the summarize-and-replace technique
  - the preamble that helps claude treat the summary as memory, not chitchat

run:
  python -m chapters.ch10_compaction          # forces compaction by stuffing context

next: ch11 — subagents (context isolation, fresh messages[]).
"""

import os
import sys

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-6"

# claude sonnet 4.5 has a 200k context. trigger compaction at 60% input usage.
CONTEXT_WINDOW = 200_000
COMPACT_TRIGGER_RATIO = 0.60
KEEP_RECENT = 4                                  # turns to keep verbatim


SUMMARIZER_PROMPT = """\
You are a conversation summarizer. Given the conversation below, write a
DENSE summary preserving:
  - active tasks and goals
  - decisions made and conclusions reached
  - identifiers (uuids, file paths, urls, names) VERBATIM
  - in-flight work the next turn must continue
Drop:
  - idle exploration, retried errors, redundant tool output
Keep it under 1000 words. Write in past tense.
"""


def count_input_tokens(messages: list[dict]) -> int:
    """Ask the API how many input tokens this messages array would cost.
    much more accurate than tiktoken/heuristics."""
    r = client.messages.count_tokens(model=MODEL, messages=messages)
    return r.input_tokens


def needs_compaction(messages: list[dict]) -> bool:
    return count_input_tokens(messages) > CONTEXT_WINDOW * COMPACT_TRIGGER_RATIO


def compact(messages: list[dict]) -> list[dict]:
    """Replace the older portion of the conversation with a single summary."""
    if len(messages) <= KEEP_RECENT + 1:
        return messages                            # nothing to compact

    # split: old (to summarize) | recent (keep verbatim)
    old, recent = messages[:-KEEP_RECENT], messages[-KEEP_RECENT:]
    print(f"  [compacting {len(old)} old messages, keeping {len(recent)} recent]")

    # ask claude to summarize the old block. note: we send `old` AS messages,
    # with a system prompt that tells claude what to preserve.
    summary_resp = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SUMMARIZER_PROMPT,
        messages=old + [{"role": "user",
                         "content": "Summarize everything above per the instructions."}],
    )
    summary_text = "".join(b.text for b in summary_resp.content if b.type == "text")
    print(f"  [summary: {len(summary_text)} chars]")

    # rebuild: one preamble user message + recent turns. the preamble framing
    # is critical — it tells claude this is memory, not a new task.
    preamble = (
        "<conversation_summary>\n"
        "The following is a summary of our conversation so far. Treat this "
        "as your memory; continue from here.\n\n"
        f"{summary_text}\n"
        "</conversation_summary>"
    )
    return [{"role": "user", "content": preamble}] + recent


def stress_test():
    """Stuff the messages array with junk until compaction triggers."""
    messages = []
    for i in range(50):
        messages.append({"role": "user",
                         "content": f"please remember fact #{i}: the value is {i*7}"})
        messages.append({"role": "assistant",
                         "content": f"got it — fact #{i} is {i*7}. " * 30})

    pre = count_input_tokens(messages)
    print(f"before compaction: {len(messages)} messages, {pre} tokens "
          f"({pre/CONTEXT_WINDOW:.0%} of window)")

    if needs_compaction(messages):
        messages = compact(messages)

    post = count_input_tokens(messages)
    print(f"after  compaction: {len(messages)} messages, {post} tokens "
          f"({post/CONTEXT_WINDOW:.0%} of window)")
    print(f"  → {pre - post} tokens saved on every future turn.")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    stress_test()
