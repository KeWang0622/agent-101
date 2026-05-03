"""
chapter 08b — observability: the dollar ticker

# Most "build an agent" tutorials ignore the question every reader asks at
# 2am: "what did this just cost me?" This chapter answers it.

claude code, cursor, openclaw all ship a token/dollar ticker. they ship it
because the #1 surprise for new agent builders is bill shock. the agent does
something simple, runs 8 turns, and you check usage and discover it cost $0.40.
on a hot loop you'll burn through your free credit overnight.

the meter you need is 30 lines. just read `response.usage` after every turn.
the four fields that matter:
  input_tokens                 — full input to this call
  output_tokens                — text + tool_use the model produced
  cache_creation_input_tokens  — tokens written to the prompt cache (5-min TTL)
  cache_read_input_tokens      — tokens read from cache (90% cheaper)

multiply by per-million prices, sum, print. that's it.

what you'll learn:
  - the four usage fields and what each one bills at
  - how to project tokens to dollars per turn
  - why prompt caching matters: typical 5-10x cost reduction on agent loops
  - how to spot a cache miss (high cache_creation, low cache_read)

run:
  python -m chapters.ch08b_observability "what's 17 * 23?"

next: ch08c — prompt caching, deep version.
"""

import os
import sys

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-5"

# claude sonnet 4.5 prices, USD per 1M tokens, april 2026.
# always check https://www.anthropic.com/pricing — these dates fast.
PRICES = {
    "input":            3.00,
    "output":          15.00,
    "cache_creation":   3.75,  # 5-minute TTL writes
    "cache_read":       0.30,  # 90% cheaper than fresh input
}


class Meter:
    """Track tokens across a session, project to USD."""
    def __init__(self):
        self.input = self.output = self.cache_create = self.cache_read = 0
        self.usd = 0.0
        self.turns = 0

    def add(self, usage) -> float:
        self.turns += 1
        i  = getattr(usage, "input_tokens", 0) or 0
        o  = getattr(usage, "output_tokens", 0) or 0
        cw = getattr(usage, "cache_creation_input_tokens", 0) or 0
        cr = getattr(usage, "cache_read_input_tokens", 0) or 0
        self.input += i
        self.output += o
        self.cache_create += cw
        self.cache_read += cr
        spent = (i  * PRICES["input"]
               + o  * PRICES["output"]
               + cw * PRICES["cache_creation"]
               + cr * PRICES["cache_read"]) / 1_000_000
        self.usd += spent
        return spent

    def report(self) -> str:
        return (
            f"turns: {self.turns}  ·  total: ${self.usd:.4f}\n"
            f"  input  {self.input:>8}  (${self.input  * PRICES['input']  / 1e6:.4f})\n"
            f"  output {self.output:>8}  (${self.output * PRICES['output'] / 1e6:.4f})\n"
            f"  cache_w{self.cache_create:>8}  (${self.cache_create * PRICES['cache_creation'] / 1e6:.4f})\n"
            f"  cache_r{self.cache_read:>8}  (${self.cache_read   * PRICES['cache_read']   / 1e6:.4f})\n"
            f"  cache hit ratio: "
            f"{(self.cache_read / max(1, self.cache_read + self.cache_create)):.1%}"
        )


# the same calculator agent as ch04, but now metered AND prompt-cached.

TOOLS = [
    {"name": "calculator",
     "description": "Evaluate a math expression like '17 * 23'.",
     "input_schema": {"type": "object",
                      "properties": {"expression": {"type": "string"}},
                      "required": ["expression"]}},
]


# NOTE: prompt caching has a MINIMUM token threshold:
#   sonnet/opus: 1024 tokens · haiku: 2048 tokens
# below the threshold, anthropic silently doesn't cache (cache_r stays 0).
# we deliberately make the system prompt long enough to cross the threshold so
# you can SEE caching working. real agents have AGENT.md or extensive tool
# instructions and clear this naturally; toy demos need padding.
SYSTEM = ("You are a careful arithmetic agent. Use the calculator tool for any "
          "arithmetic — never compute mentally. Show your work step by step.\n\n"
          "Detailed conventions for this agent (long enough to trigger caching):\n"
          + "\n".join(f"  rule {i}: always think step by step before computing, "
                      f"never assume the user means modular arithmetic, prefer "
                      f"explicit operator precedence with parentheses, return "
                      f"the result on a new line prefixed with 'answer:', and "
                      f"if the expression contains a syntactic ambiguity, list "
                      f"the two interpretations and ask the user which one."
                      for i in range(20))).strip()


def run(prompt: str, meter: Meter, *, use_cache: bool = True):
    msgs = [{"role": "user", "content": prompt}]

    # the magic: wrap system + tools with cache_control. anthropic caches the
    # prefix for ~5 min. on the second matching call, those tokens cost ~10%.
    system_param = (
        [{"type": "text", "text": SYSTEM,
          "cache_control": {"type": "ephemeral"}}]
        if use_cache else SYSTEM
    )
    tools_param = (
        [{**TOOLS[0], "cache_control": {"type": "ephemeral"}}]
        if use_cache else TOOLS
    )

    for turn in range(10):
        r = client.messages.create(
            model=MODEL, max_tokens=1024,
            system=system_param, tools=tools_param,
            messages=msgs,
        )
        spent = meter.add(r.usage)
        print(f"  turn {turn}: ${spent:.4f}  "
              f"(in={r.usage.input_tokens} out={r.usage.output_tokens} "
              f"cw={getattr(r.usage, 'cache_creation_input_tokens', 0)} "
              f"cr={getattr(r.usage, 'cache_read_input_tokens', 0)})")

        msgs.append({"role": "assistant", "content": r.content})

        for b in r.content:
            if b.type == "text" and b.text.strip():
                print(f"  claude> {b.text[:100]}{'...' if len(b.text) > 100 else ''}")

        if r.stop_reason != "tool_use":
            return

        results = []
        for b in r.content:
            if b.type == "tool_use":
                ans = str(eval(b.input["expression"], {"__builtins__": {}}))
                results.append({"type": "tool_result",
                                "tool_use_id": b.id, "content": ans})
        msgs.append({"role": "user", "content": results})


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    prompt = " ".join(sys.argv[1:]) or "what is 17 * 23, then 1234 + 5678?"

    print("--- run 1 (cache cold) ---")
    meter = Meter()
    run(prompt, meter, use_cache=True)

    print("\n--- run 2 (cache warm — same SYSTEM, new prompt) ---")
    run("what is 999 * 999?", meter, use_cache=True)

    print("\n" + meter.report())
    print("\nnotice: run 2's input cost should be ~90% lower than run 1's,")
    print("because the system prompt + tool schema were cached.")


if __name__ == "__main__":
    main()
