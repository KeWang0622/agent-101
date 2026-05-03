"""
chapter 09 — sessions: a conversation that survives `ctrl-c`

# A session is just an append-only JSONL file of the messages array.
# You can `tail -f` it. You can `cat` it. There's nothing else.

claude code calls these "sessions". the file lives at
`~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`. each line is one JSON
object. open one and you'll see the same `messages` array your loop has been
maintaining — just persisted, line by line, after every turn.

why JSONL not JSON?
  - APPEND-ONLY: you can write a line per turn without re-reading the file.
    crash-safe, fast, atomic-per-line.
  - GREPPABLE: every tool unix knows works on it. tail, grep, awk, jq.
  - SCHEMA-FREE: the format evolves; new fields don't break old readers.

what you'll learn:
  - storing messages on disk in JSONL
  - resuming a session by replaying the file into messages[]
  - the `~/.agent101/sessions/` directory layout
  - the difference between "session" (on disk) and "messages array" (in memory)

run:
  python -m chapters.ch09_sessions          # start a new session
  python -m chapters.ch09_sessions resume <id>   # resume a prior one

next: ch10 — compaction (when the messages array gets too big).
"""

import json
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-6"
SESSION_DIR = Path.home() / ".agent101" / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)


class Session:
    """An append-only JSONL log of every turn. Open once per session."""

    def __init__(self, session_id: str | None = None):
        self.id = session_id or uuid.uuid4().hex
        self.path = SESSION_DIR / f"{self.id}.jsonl"
        self.messages: list[dict] = []
        if self.path.exists():
            self._replay()                            # resume case
        else:
            self._write({"type": "meta",
                         "session_id": self.id,
                         "started": datetime.now(timezone.utc).isoformat(),
                         "cwd": os.getcwd()})

    # the only two operations: append, and replay.

    def append_user(self, text: str):
        self.messages.append({"role": "user", "content": text})
        self._write({"type": "user", "content": text})

    def append_assistant(self, content_blocks: list):
        # content_blocks comes from the SDK as objects; serialize for jsonl.
        serializable = [b.model_dump() if hasattr(b, "model_dump") else b
                        for b in content_blocks]
        self.messages.append({"role": "assistant", "content": serializable})
        self._write({"type": "assistant", "content": serializable})

    def append_tool_results(self, results: list[dict]):
        self.messages.append({"role": "user", "content": results})
        self._write({"type": "tool_results", "content": results})

    def _write(self, entry: dict):
        # one line per call. json then newline. flush so ctrl-c is safe.
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()

    def _replay(self):
        for line in self.path.open():
            entry = json.loads(line)
            t = entry["type"]
            if t == "user":            self.messages.append({"role": "user", "content": entry["content"]})
            elif t == "assistant":     self.messages.append({"role": "assistant", "content": entry["content"]})
            elif t == "tool_results":  self.messages.append({"role": "user", "content": entry["content"]})
            # meta lines are ignored on replay.


def chat_once(session: Session, prompt: str):
    session.append_user(prompt)
    r = client.messages.create(model=MODEL, max_tokens=1024,
                               messages=session.messages)
    session.append_assistant(r.content)
    for b in r.content:
        if b.type == "text":
            print(f"\nclaude> {b.text}")


def main():
    args = sys.argv[1:]
    if args and args[0] == "resume" and len(args) >= 2:
        s = Session(args[1])
        print(f"[resumed session {s.id} ({len(s.messages)} prior turns)]")
    else:
        s = Session()
        print(f"[new session {s.id}]")
        print(f"  to resume:  python -m chapters.ch09_sessions resume {s.id}")
        print(f"  on disk:    {s.path}")

    print("\nchat. ctrl-d to exit.")
    while True:
        try:
            line = input("\nyou> ")
        except EOFError:
            print()
            return
        if line.strip():
            chat_once(s, line)


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    main()
