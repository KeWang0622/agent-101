"""
chapter 15 — streaming text via server-sent events

# Streaming is engineering, not core. The agent loop works fine without it.
# But the UX is unrecognizable without streaming. So: how it works, in one file.

claude code shows tokens as they arrive. that's because the API supports SSE
(server-sent events): instead of one big response, the server sends a sequence
of tiny events, each carrying a fragment of the reply.

the SSE protocol for text-only is simple. you'll see these event types:
  message_start            — assistant message header
  content_block_start      — beginning of a block (here, type=text)
  content_block_delta      — a chunk of text. accumulate or print these.
  content_block_stop       — end of the block
  message_delta            — usage updates / final stop_reason
  message_stop             — done

we parse SSE by hand from `urllib`. the SDK has a helper, but reading the
bytes once builds the right intuition.

CRITICAL — text deltas you can render immediately. tool_use deltas you CANNOT
(they're partial JSON). that's ch16.

run:
  python -m chapters.ch15_streaming_text "explain TCP in one sentence"

next: ch16 — streaming tool_use (the hard chapter).
"""

import json
import os
import sys
import urllib.request


API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-5"


def stream(prompt: str):
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 1024,
        "stream": True,                                       # the magic flag
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )

    # SSE format: lines like `event: <name>` then `data: <json>`, separated
    # by blank lines. we read line-by-line and yield (event, data) pairs.
    with urllib.request.urlopen(req) as r:
        event = None
        for raw in r:
            line = raw.decode("utf-8").rstrip("\n")
            if line.startswith("event: "):
                event = line[len("event: "):]
            elif line.startswith("data: "):
                yield event, json.loads(line[len("data: "):])
            # blank line = event boundary; nothing to do.


def main():
    prompt = " ".join(sys.argv[1:]) or "in one sentence, what is TCP?"

    text_so_far = ""
    for event, data in stream(prompt):
        if event == "content_block_delta" and data["delta"]["type"] == "text_delta":
            chunk = data["delta"]["text"]
            text_so_far += chunk
            print(chunk, end="", flush=True)        # render as it arrives
        elif event == "message_delta":
            # the final stop_reason and full output usage land here.
            usage = data.get("usage", {})
            stop = data["delta"].get("stop_reason")
            print(f"\n\n[stop={stop} out_tokens={usage.get('output_tokens')}]")
        elif event == "message_stop":
            break


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    main()
