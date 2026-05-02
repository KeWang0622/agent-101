"""
chapter 06 — parallel tool calls

# Claude can ask for three things at once. Run all three. Send all three back.
# In one user message. Or you'll teach it to stop being parallel.

the model is allowed to emit MULTIPLE tool_use blocks in a single assistant
turn. you must:
  1. run them all (concurrently if they're slow)
  2. collect all tool_results into ONE user message

if you split into multiple user messages, claude learns from observation that
parallel calls are punished, and stops issuing them. you'll see latency
double. there's no error — just a quiet protocol-shaped loss.

what you'll learn:
  - why claude emits multiple tool_use blocks in one turn
  - the SINGLE-user-message rule (foot-gun)
  - using ThreadPoolExecutor to run them concurrently
  - measuring the latency win (3 sequential 1s tools = 3s; parallel = ~1s)

run:
  python -m chapters.ch06_parallel_tools

next: ch07 — errors, refusals, and the foot-guns.
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-5"

TOOLS = [
    {"name": "fetch_user",
     "description": "Look up a user by id. Slow (1s).",
     "input_schema": {"type": "object",
                      "properties": {"user_id": {"type": "integer"}},
                      "required": ["user_id"]}},
    {"name": "fetch_org",
     "description": "Look up an organization by id. Slow (1s).",
     "input_schema": {"type": "object",
                      "properties": {"org_id": {"type": "integer"}},
                      "required": ["org_id"]}},
    {"name": "fetch_billing",
     "description": "Look up the billing status for a user. Slow (1s).",
     "input_schema": {"type": "object",
                      "properties": {"user_id": {"type": "integer"}},
                      "required": ["user_id"]}},
]


def fake_db(name: str, args: dict) -> str:
    # pretend each tool hits a slow API. 1 second each.
    time.sleep(1.0)
    if name == "fetch_user":    return f"User {args['user_id']}: ke wang, plan=pro"
    if name == "fetch_org":     return f"Org {args['org_id']}: pika, members=12"
    if name == "fetch_billing": return f"Billing user={args['user_id']}: paid through 2026-12"
    return f"unknown tool: {name}"


def run_in_parallel(tool_uses) -> list[dict]:
    """Run every tool_use concurrently with a thread pool."""
    with ThreadPoolExecutor() as pool:
        # submit each call, remember which tool_use_id each future belongs to
        futures = [(b.id, pool.submit(fake_db, b.name, b.input))
                   for b in tool_uses if b.type == "tool_use"]
        return [{"type": "tool_result", "tool_use_id": tid, "content": fut.result()}
                for tid, fut in futures]


def agent_loop(prompt: str):
    msgs = [{"role": "user", "content": prompt}]

    for turn in range(20):
        r = client.messages.create(model=MODEL, max_tokens=1024,
                                   tools=TOOLS, messages=msgs)
        msgs.append({"role": "assistant", "content": r.content})

        for b in r.content:
            if b.type == "text" and b.text.strip():
                print(f"\nclaude> {b.text}")

        if r.stop_reason != "tool_use":
            return

        # how many tools did claude ask for THIS TURN?
        tool_uses = [b for b in r.content if b.type == "tool_use"]
        print(f"\n  [parallel: {len(tool_uses)} tools requested this turn]")

        t0 = time.time()
        results = run_in_parallel(tool_uses)
        dt = time.time() - t0
        print(f"  [completed in {dt:.2f}s — sequential would take {len(tool_uses):.1f}s]")

        # CRITICAL: ALL results in ONE user message. if you split this into
        # multiple user messages, claude observes the pattern and stops being
        # parallel on subsequent turns. silently. no error. just slower.
        msgs.append({"role": "user", "content": results})


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    agent_loop("look up user 42, their org 7, and their billing all at once. summarize.")
