"""
chapter 00 — a working agent in 30 seconds

before any theory: see one work. this file is ~30 lines. it's a complete agent
with one tool. you'll understand the loop more deeply over the next 18 chapters,
but the whole shape is right here. read it once.

  ┌────────────────┐
  │  user prompt   │
  └────────┬───────┘
           ▼
  ┌────────────────┐     ┌──────────────────┐
  │  send messages │◄────│  append result   │
  │  to claude API │     │  to messages[]   │
  └────────┬───────┘     └────────▲─────────┘
           ▼                      │
  ┌────────────────┐              │
  │  claude wants  │──── yes ─────┘
  │   a tool?      │
  └────────┬───────┘
           │ no
           ▼
       ANSWER

run:
  export ANTHROPIC_API_KEY=sk-ant-...
  python -m chapters.ch00_welcome "what's 17 * 23 then read README.md and tell me what this repo does"

next: ch01 — strip out the SDK and see one HTTP request with your own eyes.
"""

import os
import subprocess
import sys

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-5"

TOOLS = [
    {"name": "calculator", "description": "Evaluate a math expression",
     "input_schema": {"type": "object",
                      "properties": {"expression": {"type": "string"}},
                      "required": ["expression"]}},
    {"name": "bash", "description": "Run a shell command",
     "input_schema": {"type": "object",
                      "properties": {"cmd": {"type": "string"}},
                      "required": ["cmd"]}},
]


def run(name, args):
    if name == "calculator":
        return str(eval(args["expression"], {"__builtins__": {}}))
    if name == "bash":
        r = subprocess.run(args["cmd"], shell=True, capture_output=True, text=True, timeout=10)
        return (r.stdout + r.stderr)[:2000] or "(no output)"
    return f"unknown tool: {name}"


def main():
    msgs = [{"role": "user", "content": " ".join(sys.argv[1:]) or "what's 17*23?"}]

    while True:                                                    # the loop.
        r = client.messages.create(model=MODEL, max_tokens=2048, tools=TOOLS, messages=msgs)
        msgs.append({"role": "assistant", "content": r.content})

        for b in r.content:
            if b.type == "text" and b.text.strip():
                print(b.text)

        if r.stop_reason == "end_turn":
            return                                                 # done.

        # claude wants tools. run them, send back, loop.
        results = []
        for b in r.content:
            if b.type == "tool_use":
                print(f"  [{b.name}] {b.input}")
                results.append({"type": "tool_result",
                                "tool_use_id": b.id,
                                "content": run(b.name, b.input)})
        msgs.append({"role": "user", "content": results})


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    main()
