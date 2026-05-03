"""
chapter 04 — your first tool

# The model can't run code. You can. A tool is the contract between them.

we declare ONE tool (a calculator). when claude wants to use it, we:
  1. parse the `tool_use` block from the reply
  2. run the tool locally
  3. send the result back as a `tool_result` block in a NEW user message
  4. (in ch05 we wrap this in `while True`)

what you'll learn:
  - tool schema (json schema input, name, description)
  - the tool_use → tool_result protocol
  - the foot-gun: tool_result blocks must IMMEDIATELY follow their tool_use.
    you cannot put any other message in between, or the API rejects it.

run:
  python -m chapters.ch04_one_tool "what is 17 * 23?"

next: ch05 — formalize the loop. the canonical 6 lines that are every agent.
"""

import os
import sys

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-5"

# a tool definition is just a dict. `input_schema` is JSON Schema — the model
# uses it to decide when to call this tool and what args to pass.
TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluates a math expression. Use for any arithmetic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Python-syntax expression, e.g. '17 * 23'.",
                },
            },
            "required": ["expression"],
        },
    },
]


def run_tool(name: str, args: dict) -> str:
    # the tool's job: take args, return a string. real tools might read files,
    # query a db, or hit an API. ours evaluates math. that's enough.
    if name == "calculator":
        # `eval` is dangerous in production. fine here for one chapter.
        return str(eval(args["expression"], {"__builtins__": {}}))
    return f"unknown tool: {name}"


def agent_loop(prompt: str):
    messages = [{"role": "user", "content": prompt}]

    while True:
        r = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": r.content})

        # the natural exit: claude has nothing more to say, no tool to call.
        if r.stop_reason == "end_turn":
            for block in r.content:
                if block.type == "text":
                    print(f"\nclaude> {block.text}")
            return

        # the loop case: claude wants to call a tool. find every tool_use block
        # in the reply, run each one, collect the results into a single
        # user message of tool_result blocks.
        if r.stop_reason == "tool_use":
            tool_results = []
            for block in r.content:
                if block.type == "tool_use":
                    print(f"  [tool] {block.name}({block.input})")
                    result = run_tool(block.name, block.input)
                    print(f"  [tool] -> {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,           # link to the call
                        "content": result,
                    })
            # FOOT-GUN: this user message must come RIGHT AFTER the assistant
            # message with the tool_use blocks. no other messages in between.
            messages.append({"role": "user", "content": tool_results})
            continue

        # any other stop_reason: bail. ch03 covers what they mean.
        raise RuntimeError(f"unexpected stop_reason: {r.stop_reason}")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    prompt = " ".join(sys.argv[1:]) or "what is 1234 * 5678?"
    agent_loop(prompt)
