"""
chapter 07 — errors, refusals, and the foot-guns

# A tool that crashes is a bug. A tool that returns its error as a string is
# graceful degradation. The agent loop must never raise on a tool error.

four classes of failure your loop will see in production:

  1. tool raised an exception (FileNotFoundError, timeout, etc.)
     → catch it, return the error AS A STRING, set is_error=True.
       claude will see the error and recover.

  2. claude called a tool that doesn't exist
     → return "unknown tool: <name>". claude apologizes and tries another.

  3. claude tried to call a tool with wrong args (missing required, wrong type)
     → the SDK throws on the next API call. catch, retry once, then give up.

  4. stop_reason="refusal" / "max_tokens" / "pause_turn"
     → not tool_use. each requires its own handling. don't lump them with end_turn.

the rule: NEVER let an exception kill the loop. you've already paid for
the tokens to get here. burn one more turn, let claude recover.

run:
  python -m chapters.ch07_errors

next: ch08 — system prompts (and what to put where).
"""

import os
import sys

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-6"

TOOLS = [
    {"name": "divide",
     "description": "Compute a/b. Errors on division by zero.",
     "input_schema": {"type": "object",
                      "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                      "required": ["a", "b"]}},
    {"name": "weather",
     "description": "Get weather for a city. (Stub: only knows 'sf'.)",
     "input_schema": {"type": "object",
                      "properties": {"city": {"type": "string"}},
                      "required": ["city"]}},
]


def dispatch(name: str, args: dict) -> tuple[str, bool]:
    """Returns (content, is_error). is_error=True is a hint to the model."""
    try:
        if name == "divide":
            return str(args["a"] / args["b"]), False
        if name == "weather":
            db = {"sf": "62F partly cloudy"}
            if args["city"] not in db:
                return f"unknown city: {args['city']}. known: {list(db)}", True
            return db[args["city"]], False
        return f"unknown tool: {name}", True
    except Exception as e:
        # NEVER let this kill the loop. tell claude what happened.
        return f"{type(e).__name__}: {e}", True


def agent_loop(prompt: str):
    msgs = [{"role": "user", "content": prompt}]

    for turn in range(15):
        r = client.messages.create(model=MODEL, max_tokens=1024,
                                   tools=TOOLS, messages=msgs)
        msgs.append({"role": "assistant", "content": r.content})

        for b in r.content:
            if b.type == "text" and b.text.strip():
                print(f"\nclaude> {b.text}")

        # exhaustive stop_reason handling. don't conflate the cases.
        if r.stop_reason == "end_turn":
            return
        if r.stop_reason == "max_tokens":
            print("\n[truncated at max_tokens — usually means a tool result was huge]")
            return
        if r.stop_reason == "stop_sequence":
            return
        if r.stop_reason == "refusal":
            print("\n[claude refused — surface this to the user]")
            return
        if r.stop_reason == "pause_turn":
            # server tools / long actions can pause. just send back to continue.
            continue
        if r.stop_reason != "tool_use":
            print(f"\n[unknown stop_reason: {r.stop_reason}]")
            return

        results = []
        for b in r.content:
            if b.type == "tool_use":
                content, is_err = dispatch(b.name, b.input)
                marker = "✗" if is_err else "✓"
                print(f"  {marker} {b.name}({b.input}) -> {content}")
                results.append({"type": "tool_result",
                                "tool_use_id": b.id,
                                "content": content,
                                "is_error": is_err})        # the magic flag
        msgs.append({"role": "user", "content": results})


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    # prompt forces three failures: division by zero, unknown city, then
    # claude must recover and answer with what works.
    agent_loop("what's 10 / 0, then weather in tokyo, then weather in sf?")
