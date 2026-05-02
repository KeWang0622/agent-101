# Chapter 09 — Sessions: A Conversation That Survives `Ctrl-C` 🐢

> **A session is just an append-only JSONL file of the messages array. You can `tail -f` it. You can `cat` it. There's nothing else.**

## 🐢 GuiGui says

Claude Code, Cursor, openclaw — they all use the same trick. JSONL on disk, one line per turn. Open one and you'll see the same `messages` array your loop has been maintaining, persisted line by line.

## Why JSONL not JSON

| Feature | JSON | JSONL |
|---|---|---|
| Append per turn | Read + parse + modify + write | One `f.write(line + "\n")` |
| Crash mid-write | Corrupt array | One bad line; rest survive |
| Greppable / `tail -f` | No | Yes |
| Schema evolution | Breaks old readers | Independent lines |

## Show me the code

```python
class Session:
    def __init__(self, session_id=None):
        self.id = session_id or uuid.uuid4().hex
        self.path = SESSION_DIR / f"{self.id}.jsonl"
        self.messages = []
        if self.path.exists():
            for line in self.path.open():
                self._reload(json.loads(line))

    def append(self, role, content):
        self.messages.append({"role": role, "content": content})
        with self.path.open("a") as f:
            f.write(json.dumps({"role": role, "content": content}) + "\n")
```

## ⚠️ Watch out for

**The orphan user message.** Ctrl-C between user prompt and assistant reply leaves an orphan. On `--resume`, the next API call rejects with role-alternation 400. Fix: walk the array on resume; if last is bare-string user, pop it.

## ✅ Summary

- JSONL: append-only, crash-safe, greppable, atomic per line.
- Session = file + in-memory mirror of messages.
- Resume = replay file into memory; truncate orphans.

## 📝 Homework

```bash
# start a session, kill it mid-turn, resume
python -m chapters.ch09_sessions
> hello
> what's 2+2?
> ^C
python -m chapters.ch09_sessions resume <id>
> what did I just ask?
```

1. Verify the resumed session remembers your prior turns.
2. `tail -f ~/.agent101/sessions/<id>.jsonl` while running. Watch each turn append.
3. Modify ONE line in the JSONL by hand. Resume. Does it work?

## 🚀 Next

[Chapter 10 — Compaction](ch10_compaction.md): the array grows forever. Until it doesn't.
