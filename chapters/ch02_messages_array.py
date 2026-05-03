"""
chapter 02 — the messages array IS the memory

the most common confusion when starting with LLM APIs:
  > "why does the model forget what I just told it?"

answer: because the API is stateless. every call is independent. if you want
multi-turn, YOU send the entire conversation history every time.

the `messages` array IS the memory. there is no other memory. when claude code
"remembers" your prior turn, it's because the python process kept the array
in a variable and re-sent it.

what you'll learn:
  - alternating user/assistant role pattern
  - how to append the assistant's reply back into messages
  - why the array grows linearly (and why that becomes a problem — see ch10)

run:
  python -m chapters.ch02_messages_array

next: ch03 — stop reasons (the way OUT of the loop).
"""

import os
import sys

from anthropic import Anthropic


client = Anthropic()  # picks up ANTHROPIC_API_KEY from env
MODEL = "claude-sonnet-4-5"


def chat_loop():
    # `messages` is just a list of dicts. it starts empty. it grows.
    # there is no Conversation object, no Session class, nothing fancy.
    messages: list[dict] = []

    while True:
        try:
            user_input = input("\nyou> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input.strip():
            continue

        # 1. append the user's turn.
        messages.append({"role": "user", "content": user_input})

        # 2. send the ENTIRE history. the model sees turns 1..N every call.
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=messages,
        )

        # 3. append the assistant's reply so the next call has it as context.
        # response.content is a list of content blocks (see ch01). we pass the
        # whole list back — that's what the API expects on the next turn.
        messages.append({"role": "assistant", "content": response.content})

        # 4. print the text. (in ch03 we'll print as it streams.)
        for block in response.content:
            if block.type == "text":
                print(f"\nclaude> {block.text}")

        # the messages array now has 2N items after N turns. notice how
        # quickly it grows. that's chapter 10 (compaction).
        print(f"  [messages.len={len(messages)}, "
              f"in={response.usage.input_tokens}, "
              f"out={response.usage.output_tokens}]", file=sys.stderr)


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    print("multi-turn chat. ctrl-d to exit.")
    chat_loop()
