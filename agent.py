"""
agent.py — the climax. a Claude-Code-shaped CLI agent in ~600 lines.

# By chapter 17 you understood every primitive. This file uses them all.

it has six tools (Read, Write, Edit, Bash, Glob, Grep) plus TodoWrite for
multi-step planning. it streams output, renders tool calls in boxes, shows
unified diffs for Edit, persists sessions as JSONL, supports five slash
commands, loads AGENT.md context from your repo, and asks before touching
the filesystem.

run:
  python agent.py "build me a tetris game in one html file and open it"
  python agent.py --resume <session-id>
  python agent.py                                    # interactive REPL

the file is intentionally one file. you should be able to read it on a flight.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax


# ============================================================
# 1. config
# ============================================================

MODEL = os.environ.get("AGENT101_MODEL", "claude-sonnet-4-5")
MAX_TURNS = 50
SESSION_DIR = Path.home() / ".agent101" / "projects"
DEFAULT_PERMISSION = os.environ.get("AGENT101_PERMISSION", "ask")  # ask|allow|deny
console = Console()


# ============================================================
# 2. tools
# ============================================================

def tool_read(file_path: str, **_):
    p = Path(file_path)
    if not p.exists():
        return f"ERROR: no such file: {file_path}"
    body = p.read_text()
    return body[:50_000]


def tool_write(file_path: str, content: str, **_):
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"wrote {len(content)} chars to {file_path}"


def tool_edit(file_path: str, old_string: str, new_string: str, **_):
    p = Path(file_path)
    body = p.read_text()
    if old_string not in body:
        return f"ERROR: old_string not found in {file_path}"
    if body.count(old_string) > 1:
        return f"ERROR: old_string appears {body.count(old_string)} times — make it unique"
    new_body = body.replace(old_string, new_string)
    p.write_text(new_body)
    return _diff_summary(file_path, body, new_body)


def tool_bash(command: str, **_):
    try:
        r = subprocess.run(command, shell=True, capture_output=True,
                           text=True, timeout=120)
        out = (r.stdout + r.stderr)[:20_000]
        return out or "(no output)"
    except subprocess.TimeoutExpired:
        return "ERROR: command timed out after 120s"


def tool_glob(pattern: str, path: str = ".", **_):
    matches = sorted(Path(path).glob(pattern))
    return "\n".join(str(p) for p in matches[:200]) or "(no matches)"


def tool_grep(pattern: str, path: str = ".", **_):
    try:
        r = subprocess.run(["rg", "-n", pattern, path], capture_output=True,
                           text=True, timeout=10)
        return r.stdout[:20_000] or "(no matches)"
    except FileNotFoundError:
        # fallback to grep -rn if ripgrep isn't installed.
        r = subprocess.run(["grep", "-rn", pattern, path], capture_output=True,
                           text=True, timeout=10)
        return r.stdout[:20_000] or "(no matches)"


def tool_todo_write(todos: list, **_):
    rendered = "\n".join(f"  [{t.get('status','pending')[0].upper()}] {t['content']}"
                         for t in todos)
    return f"todos updated:\n{rendered}"


TOOLS = [
    {"name": "Read",
     "description": "Read a file's full contents.",
     "input_schema": {"type": "object",
                      "properties": {"file_path": {"type": "string"}},
                      "required": ["file_path"]}},
    {"name": "Write",
     "description": "Write a file. Creates parent directories. Overwrites if exists.",
     "input_schema": {"type": "object",
                      "properties": {"file_path": {"type": "string"},
                                     "content": {"type": "string"}},
                      "required": ["file_path", "content"]}},
    {"name": "Edit",
     "description": "Replace exact string old_string with new_string in a file. "
                    "old_string must appear EXACTLY ONCE in the file.",
     "input_schema": {"type": "object",
                      "properties": {"file_path": {"type": "string"},
                                     "old_string": {"type": "string"},
                                     "new_string": {"type": "string"}},
                      "required": ["file_path", "old_string", "new_string"]}},
    {"name": "Bash",
     "description": "Execute a bash command. Output truncated to 20KB.",
     "input_schema": {"type": "object",
                      "properties": {"command": {"type": "string"}},
                      "required": ["command"]}},
    {"name": "Glob",
     "description": "Find files matching a glob pattern (e.g. '**/*.py').",
     "input_schema": {"type": "object",
                      "properties": {"pattern": {"type": "string"},
                                     "path": {"type": "string"}},
                      "required": ["pattern"]}},
    {"name": "Grep",
     "description": "Search file contents with a regex (uses ripgrep if available).",
     "input_schema": {"type": "object",
                      "properties": {"pattern": {"type": "string"},
                                     "path": {"type": "string"}},
                      "required": ["pattern"]}},
    {"name": "TodoWrite",
     "description": "Track a multi-step plan. Call this when starting a task with "
                    "more than 2 steps. Each todo has 'content' and 'status' "
                    "(pending|in_progress|completed).",
     "input_schema": {"type": "object",
                      "properties": {"todos": {"type": "array",
                                               "items": {"type": "object"}}},
                      "required": ["todos"]}},
]

DISPATCH = {
    "Read":      tool_read,
    "Write":     tool_write,
    "Edit":      tool_edit,
    "Bash":      tool_bash,
    "Glob":      tool_glob,
    "Grep":      tool_grep,
    "TodoWrite": tool_todo_write,
}

# tools that ask permission before running
WRITE_TOOLS = {"Write", "Edit", "Bash"}


# ============================================================
# 3. rendering
# ============================================================

def render_tool_call(name: str, args: dict):
    label = _tool_label(name, args)
    console.print(f"[bold green]●[/bold green] {label}")


def render_tool_result(name: str, result: str):
    if result.startswith("ERROR"):
        console.print(f"  [red]⎿  {result.splitlines()[0]}[/red]")
        return
    if name == "Edit":
        # the result already contains a unified diff (from _diff_summary)
        for line in result.splitlines()[:30]:
            color = ("green" if line.startswith("+") and not line.startswith("+++")
                     else "red" if line.startswith("-") and not line.startswith("---")
                     else "default")
            console.print(f"  ⎿  [{color}]{line}[/{color}]")
        return
    lines = result.splitlines()
    show = lines[:8]
    for line in show:
        console.print(f"  ⎿  {line}")
    if len(lines) > len(show):
        console.print(f"  ⎿  [dim]... ({len(lines) - len(show)} more lines)[/dim]")


def _tool_label(name: str, args: dict) -> str:
    if name == "Bash":      return f"Bash$ {args.get('command','')[:80]}"
    if name == "Read":      return f"Read({args.get('file_path','')})"
    if name == "Write":     return f"Write({args.get('file_path','')})"
    if name == "Edit":      return f"Edit({args.get('file_path','')})"
    if name == "Glob":      return f"Glob({args.get('pattern','')})"
    if name == "Grep":      return f"Grep({args.get('pattern','')})"
    if name == "TodoWrite": return f"TodoWrite ({len(args.get('todos',[]))} items)"
    return f"{name}({args})"


def _diff_summary(path: str, before: str, after: str) -> str:
    diff = difflib.unified_diff(before.splitlines(), after.splitlines(),
                                fromfile=path, tofile=path, lineterm="", n=2)
    return "\n".join(list(diff)[:40])


def render_text(text: str):
    if text.strip():
        console.print(Markdown(text))


# ============================================================
# 4. permissions
# ============================================================

def ask_permission(name: str, args: dict) -> bool:
    if DEFAULT_PERMISSION == "allow":
        return True
    if DEFAULT_PERMISSION == "deny":
        return False
    # default: ask
    label = _tool_label(name, args)
    console.print(f"\n[yellow]allow {label}? [Y/n][/yellow] ", end="")
    answer = input().strip().lower()
    return answer in ("", "y", "yes")


# ============================================================
# 5. AGENT.md loader
# ============================================================

def load_agent_md(start: Path) -> str:
    """Walk up from cwd, collect AGENT.md files (root-first, deepest-last)."""
    parts = []
    p = start.resolve()
    chain = [p] + list(p.parents)
    chain.reverse()                 # root first
    for d in chain:
        candidate = d / "AGENT.md"
        if candidate.is_file():
            parts.append(f"# from {candidate}\n{candidate.read_text()}")
    user = Path.home() / ".agent101" / "AGENT.md"
    if user.is_file():
        parts.insert(0, f"# user-scope ({user})\n{user.read_text()}")
    return "\n\n".join(parts)[:25_000]


# ============================================================
# 6. sessions
# ============================================================

class Session:
    def __init__(self, session_id: str | None = None, cwd: Path | None = None):
        self.id = session_id or uuid.uuid4().hex[:12]
        self.cwd = cwd or Path.cwd()
        slug = str(self.cwd).replace("/", "-").lstrip("-")
        self.dir = SESSION_DIR / slug
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / f"{self.id}.jsonl"
        self.messages: list[dict] = []
        if self.path.exists():
            self._replay()
        else:
            self._write({"type": "meta", "session_id": self.id,
                         "started": datetime.now(timezone.utc).isoformat(),
                         "cwd": str(self.cwd)})

    def append_user(self, text: str):
        self.messages.append({"role": "user", "content": text})
        self._write({"type": "user", "content": text})

    def append_assistant(self, content_blocks):
        ser = [b.model_dump() if hasattr(b, "model_dump") else b for b in content_blocks]
        self.messages.append({"role": "assistant", "content": ser})
        self._write({"type": "assistant", "content": ser})

    def append_tool_results(self, results: list[dict]):
        self.messages.append({"role": "user", "content": results})
        self._write({"type": "tool_results", "content": results})

    def clear(self):
        self.messages.clear()
        # we keep the file for audit; just stop using its contents.

    def _write(self, entry: dict):
        with self.path.open("a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
            f.flush()

    def _replay(self):
        for line in self.path.open():
            entry = json.loads(line)
            t = entry["type"]
            if t == "user":
                self.messages.append({"role": "user", "content": entry["content"]})
            elif t == "assistant":
                self.messages.append({"role": "assistant", "content": entry["content"]})
            elif t == "tool_results":
                self.messages.append({"role": "user", "content": entry["content"]})


# ============================================================
# 7. compaction
# ============================================================

CONTEXT_WINDOW = 200_000
COMPACT_TRIGGER = 0.60
KEEP_RECENT = 6

SUMMARIZER = ("You are summarizing a conversation. Preserve identifiers, file paths, "
              "active tasks, decisions, and pending TODOs verbatim. Drop redundant "
              "tool output and idle exploration. Past tense. Under 1000 words.")


def compact_messages(client: Anthropic, messages: list[dict]) -> list[dict]:
    if len(messages) <= KEEP_RECENT + 1:
        return messages
    old, recent = messages[:-KEEP_RECENT], messages[-KEEP_RECENT:]
    console.print(f"  [dim]compacting {len(old)} old messages...[/dim]")
    r = client.messages.create(
        model=MODEL, max_tokens=2048, system=SUMMARIZER,
        messages=old + [{"role": "user",
                         "content": "Summarize everything above per instructions."}],
    )
    summary = "".join(b.text for b in r.content if b.type == "text")
    preamble = ("<conversation_summary>\nThe following is a summary of our prior "
                f"conversation; treat as memory.\n\n{summary}\n</conversation_summary>")
    return [{"role": "user", "content": preamble}] + recent


# ============================================================
# 8. slash commands
# ============================================================

def handle_slash(client: Anthropic, session: Session, cmd: str, args: str) -> bool:
    """Return True if the command consumed the line (no LLM call)."""
    if cmd == "/help":
        console.print("[bold]commands:[/bold]")
        console.print("  /help                 show this")
        console.print("  /clear                forget conversation; keep file")
        console.print("  /compact              summarize and continue")
        console.print("  /resume <id>          load another session")
        console.print("  /exit                 quit (or ctrl-d)")
        return True
    if cmd == "/clear":
        session.clear()
        console.print("  [dim]cleared.[/dim]")
        return True
    if cmd == "/compact":
        session.messages = compact_messages(client, session.messages)
        console.print("  [dim]compacted.[/dim]")
        return True
    if cmd == "/resume":
        # caller should restart via main(); we just print the path.
        console.print(f"  [dim]restart with: python agent.py --resume {args}[/dim]")
        return True
    if cmd == "/exit":
        sys.exit(0)
    return False


# ============================================================
# 9. the agent loop
# ============================================================

DEFAULT_SYSTEM = """\
You are agent-101, a minimal coding agent that runs in the user's terminal.
You are an educational reference implementation — about 600 lines of Python
wrapping the Anthropic Messages API in a tool-use loop. Be precise and terse.

You have these tools: Read, Write, Edit, Bash, Glob, Grep, TodoWrite.

Workflow on any task:
  1. Gather context (Read, Glob, Grep) before acting.
  2. For multi-step work, call TodoWrite first to plan.
  3. Take action (Write/Edit/Bash) — these will prompt the user for permission.
  4. Verify your work (run tests, open the result, read the output).

Rules:
  - Read a file BEFORE editing it.
  - Never invent file paths — discover them with Glob or `ls`.
  - When a command fails, read the error and try one fix; if it fails again, ask.
  - Prefer small surgical Edits over wholesale rewrites.
  - Keep responses short. The user is reading the source code as they use you."""


def agent_turn(client: Anthropic, session: Session, system: str, user_input: str):
    session.append_user(user_input)

    for turn in range(MAX_TURNS):
        try:
            r = client.messages.create(
                model=MODEL, max_tokens=4096,
                system=system, tools=TOOLS, messages=session.messages,
            )
        except Exception as e:
            console.print(f"[red]API error: {e}[/red]")
            return

        session.append_assistant(r.content)

        # render any text claude produced
        text = "".join(b.text for b in r.content if b.type == "text")
        render_text(text)

        if r.stop_reason != "tool_use":
            return

        # dispatch each tool_use, optionally asking for permission
        results = []
        for b in r.content:
            if b.type != "tool_use":
                continue
            render_tool_call(b.name, b.input)

            if b.name in WRITE_TOOLS and not ask_permission(b.name, b.input):
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": "user denied this tool call.",
                                "is_error": True})
                continue

            handler = DISPATCH.get(b.name)
            if handler is None:
                out = f"unknown tool: {b.name}"
            else:
                try:
                    out = handler(**b.input)
                except Exception as e:
                    out = f"ERROR: {type(e).__name__}: {e}"

            render_tool_result(b.name, out)
            results.append({"type": "tool_result",
                            "tool_use_id": b.id, "content": out})

        session.append_tool_results(results)


# ============================================================
# 10. main
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="*")
    ap.add_argument("--resume", help="resume session by id")
    ap.add_argument("--session-dir", action="store_true", help="print session dir and exit")
    args = ap.parse_args()

    if args.session_dir:
        print(SESSION_DIR)
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")

    client = Anthropic()
    session = Session(session_id=args.resume)

    # build the system prompt: default + AGENT.md
    agent_md = load_agent_md(Path.cwd())
    system = DEFAULT_SYSTEM + ("\n\n# project context (AGENT.md)\n" + agent_md
                                if agent_md else "")

    console.print(Panel.fit(
        f"[bold]agent-101[/bold]  •  [dim]session {session.id}[/dim]\n"
        f"[dim]model {MODEL}  •  cwd {Path.cwd()}[/dim]",
        border_style="dim"))

    if args.prompt:
        agent_turn(client, session, system, " ".join(args.prompt))
        return

    # interactive REPL
    console.print("[dim]/help for commands, ctrl-d to exit[/dim]\n")
    while True:
        try:
            line = console.input("[bold blue]>[/bold blue] ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line.strip():
            continue
        if line.startswith("/"):
            cmd, _, rest = line.partition(" ")
            if handle_slash(client, session, cmd, rest):
                continue
        agent_turn(client, session, system, line)


if __name__ == "__main__":
    main()
