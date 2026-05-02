"""
chapter 05 — THE LOOP

# The thing the model can't do is run code. The thing you can't do is think.
# An agent loop is just `while True` of one talking to the other.

this is the chapter the entire course pivots on. everything before it built up
to a single insight. everything after it adds layers around it. the loop itself
is six lines. read it slowly.

  while True:
      r = client.messages.create(model=M, messages=msgs, tools=TOOLS)
      msgs.append({"role": "assistant", "content": r.content})
      if r.stop_reason != "tool_use":
          return r
      msgs.append({"role": "user", "content": run_all_tools(r.content)})

that's it. that's claude code. that's cursor. that's devin. all the rest is
craft: better tools, better rendering, better memory management, better
sandboxes. the loop never changes.

what you'll learn:
  - the canonical 6-line agent loop
  - WHY this works: the model is stateless, you carry state, tools talk back
  - why a `for _ in range(MAX)` cap is non-negotiable (the runaway-loop horror)
  - what "an agent" actually is (it's a structural pattern, not a model)

we add three real tools (read, glob, bash) so the loop has work to do, and
ask a question that requires calling them in sequence. read the trace.

run:
  python -m chapters.ch05_the_loop "what's the biggest python file in chapters/?"

next: ch06 — parallel tool calls.
"""

import os
import subprocess
import sys
from pathlib import Path

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-5"
MAX_TURNS = 25                         # the runaway-loop guard. always set this.

TOOLS = [
    {"name": "glob",
     "description": "List files matching a glob pattern (e.g. '*.py').",
     "input_schema": {"type": "object",
                      "properties": {"pattern": {"type": "string"}},
                      "required": ["pattern"]}},
    {"name": "read_file",
     "description": "Return the contents of a file (truncated to 4KB).",
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"}},
                      "required": ["path"]}},
    {"name": "bash",
     "description": "Run a bash command. Output truncated to 4KB.",
     "input_schema": {"type": "object",
                      "properties": {"cmd": {"type": "string"}},
                      "required": ["cmd"]}},
]


def dispatch(name: str, args: dict) -> str:
    try:
        if name == "glob":
            return "\n".join(str(p) for p in Path(".").glob(args["pattern"])) or "(no matches)"
        if name == "read_file":
            return Path(args["path"]).read_text()[:4000]
        if name == "bash":
            r = subprocess.run(args["cmd"], shell=True, capture_output=True,
                               text=True, timeout=10)
            return (r.stdout + r.stderr)[:4000] or "(no output)"
        return f"unknown tool: {name}"
    except Exception as e:
        # tool errors must NEVER raise. return the error AS A STRING so the
        # model can read it, learn from it, and try something else. ch07 dives
        # into this.
        return f"ERROR: {type(e).__name__}: {e}"


def run_all_tools(content_blocks) -> list[dict]:
    """Run every tool_use block in one assistant turn, collect tool_results."""
    results = []
    for b in content_blocks:
        if b.type == "tool_use":
            print(f"  → {b.name}({b.input})")
            out = dispatch(b.name, b.input)
            print(f"    {out[:120]}{'...' if len(out) > 120 else ''}")
            results.append({"type": "tool_result",
                            "tool_use_id": b.id, "content": out})
    return results


def agent_loop(prompt: str):
    msgs = [{"role": "user", "content": prompt}]

    for turn in range(MAX_TURNS):
        r = client.messages.create(model=MODEL, max_tokens=2048,
                                   tools=TOOLS, messages=msgs)
        msgs.append({"role": "assistant", "content": r.content})

        # let the model think out loud — print any text it produced this turn.
        for b in r.content:
            if b.type == "text" and b.text.strip():
                print(f"\nclaude> {b.text}")

        if r.stop_reason != "tool_use":
            print(f"\n[done in {turn + 1} turns; stop={r.stop_reason}]")
            return

        msgs.append({"role": "user", "content": run_all_tools(r.content)})

    print(f"\n[hit MAX_TURNS={MAX_TURNS}]")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    prompt = " ".join(sys.argv[1:]) or "what's the biggest python file in chapters/, by line count?"
    agent_loop(prompt)
