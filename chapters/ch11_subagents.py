"""
chapter 11 — subagents (context isolation as a feature)

# A subagent is an agent loop with a FRESH messages array, called as a tool.
# Its conversation is invisible to the parent. Only its final answer comes back.

why bother? the parent's context is precious. if you ask the parent to "list
every python file and read each one to find the one with the most TODOs", the
parent's messages array fills up with file contents you'll never reference
again. spawn a subagent: it does the search, reads everything, returns
"src/foo.py has 17 TODOs". 17 tokens back, instead of 17,000.

this is the load-bearing trick behind claude code's `Task` tool and
openclaw's subagents. it's what makes coding agents handle huge repos.

cost math:
  same problem, single agent:  ~50,000 input tokens/turn × 10 turns = 500k
  same problem, with subagent: ~5,000 input tokens/turn × 10 turns = 50k
  10x cheaper. and the parent stays sharp because its context is uncluttered.

what you'll learn:
  - registering "Task" as a meta-tool that spawns a child loop
  - passing a description and a system prompt down
  - returning only the FINAL ANSWER to the parent
  - when to spawn (whenever you'd otherwise dump 5k+ tokens of context)

run:
  python -m chapters.ch11_subagents

next: ch12 — skills (markdown loaded on demand).
"""

import os
import subprocess
import sys

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-5"


# --- the subagent's own tools (small set, focused) ----------------------

SUBAGENT_TOOLS = [
    {"name": "bash",
     "description": "Run a shell command.",
     "input_schema": {"type": "object",
                      "properties": {"cmd": {"type": "string"}},
                      "required": ["cmd"]}},
]


def subagent_dispatch(name: str, args: dict) -> str:
    if name == "bash":
        r = subprocess.run(args["cmd"], shell=True, capture_output=True,
                           text=True, timeout=20)
        return (r.stdout + r.stderr)[:8000] or "(no output)"
    return f"unknown tool: {name}"


def run_subagent(task: str, system: str = "") -> str:
    """Run a fresh agent loop. Return only the final assistant text."""
    msgs = [{"role": "user", "content": task}]
    final_text = ""

    for _ in range(20):                              # subagent has its own cap
        r = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system or "You are a focused subagent. Be terse.",
            tools=SUBAGENT_TOOLS,
            messages=msgs,
        )
        msgs.append({"role": "assistant", "content": r.content})
        final_text = "".join(b.text for b in r.content if b.type == "text")

        if r.stop_reason != "tool_use":
            break

        msgs.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": b.id,
             "content": subagent_dispatch(b.name, b.input)}
            for b in r.content if b.type == "tool_use"
        ]})

    return final_text or "(subagent had no final answer)"


# --- the parent's tools (one of which is Task, the spawn meta-tool) ------

PARENT_TOOLS = [
    {"name": "Task",
     "description": (
         "Delegate a self-contained subtask to a fresh subagent. Use this "
         "when a question would require reading lots of files or running "
         "many commands you won't reference later. Returns only the final "
         "answer (not the subagent's intermediate work)."
     ),
     "input_schema": {
         "type": "object",
         "properties": {
             "description": {"type": "string",
                             "description": "What the subagent should accomplish."},
         },
         "required": ["description"],
     }},
]


def parent_loop(prompt: str):
    msgs = [{"role": "user", "content": prompt}]

    for turn in range(10):
        r = client.messages.create(model=MODEL, max_tokens=2048,
                                   tools=PARENT_TOOLS, messages=msgs)
        msgs.append({"role": "assistant", "content": r.content})

        for b in r.content:
            if b.type == "text" and b.text.strip():
                print(f"\nparent> {b.text}")

        if r.stop_reason != "tool_use":
            return

        results = []
        for b in r.content:
            if b.type == "tool_use" and b.name == "Task":
                desc = b.input["description"]
                print(f"\n  ▶ spawning subagent: {desc[:80]}")
                answer = run_subagent(desc)
                print(f"  ◀ subagent returned: {answer[:200]}")
                results.append({"type": "tool_result",
                                "tool_use_id": b.id,
                                "content": answer})
        msgs.append({"role": "user", "content": results})


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    # a question that would blow the parent's context if it tried to do it
    # itself — but is one bullet of summary if delegated.
    parent_loop("delegate to a subagent: find the longest python file in chapters/ "
                "and tell me how many lines it is. just the answer.")
