"""
chapter 01 — the rawest thing you can do with the anthropic api

an "agent" is, ultimately, a while-loop wrapped around an HTTP request. before
we get to the loop, let's see what one request actually looks like — no SDK, no
framework, just `requests.post`. if you've used the anthropic SDK before, this
might surprise you with how little is going on.

what you'll learn:
  - the messages API endpoint
  - the four required fields (model, max_tokens, messages, system)
  - the response shape (content blocks, stop_reason, usage)
  - that the API is STATELESS. it has no memory of any prior call.

run:
  export ANTHROPIC_API_KEY=sk-ant-...
  python -m chapters.ch01_raw_call

next: ch02 — multi-turn (we'll watch the messages array grow).

# the API has no memory. we keep state in `messages`. that single sentence
# is the entire conceptual leap of building agents from raw API calls.
"""

import json
import os
import sys
import urllib.request


API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-5"


def call(prompt: str) -> dict:
    # we deliberately use urllib instead of `anthropic` or `requests` so you
    # see there is nothing magical here. it is one HTTP POST with a JSON body.
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 1024,
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
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def main():
    prompt = " ".join(sys.argv[1:]) or "in one sentence, what is an agent?"
    response = call(prompt)

    # the response is a JSON object with these keys:
    #   id, type, role, model, content, stop_reason, stop_sequence, usage
    #
    # `content` is a LIST of "content blocks". for plain text replies, there's
    # one block of type "text". later we'll see "tool_use" and "thinking" blocks.
    print(json.dumps(response, indent=2))

    # the actual reply text:
    print("\n--- model said ---")
    for block in response["content"]:
        if block["type"] == "text":
            print(block["text"])

    # the model has NO MEMORY of this call. if you call it again, the
    # conversation does not continue — you have to send the prior turns yourself.
    # that's chapter 2.
    print(f"\nstop_reason: {response['stop_reason']}")
    print(f"usage: {response['usage']}")


if __name__ == "__main__":
    main()
