"""
microsite — the capstone. build a working landing page from one prompt.

  $ python microsite/build_site.py "a Brooklyn ramen shop called Sazae"
  → planning... 4 files
  → writing index.html
  → opened in browser
  ✓ done in 47s

uses every primitive built in chapters 1–17:
  - the agent loop (ch05)
  - parallel tool calls (ch06) — write multiple files at once
  - errors (ch07) — graceful degradation when CSS parses fail
  - system prompt (ch08) — the "landing-page" skill is loaded
  - sessions (ch09) — replays the build later if needed
  - subagents (ch11) — one for HTML, one for the copy
  - skills (ch12) — landing-page/SKILL.md gets loaded automatically

at the end, the agent runs `open index.html` (macOS) or `xdg-open` (linux).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# we reuse agent.py's loop + tools verbatim. the only specialization here is
# the system prompt + a different output directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent import (
    Anthropic, Session, agent_turn, load_agent_md, MODEL,
    console, Panel,
)


SYSTEM_OVERRIDE = """\
You are a microsite-building agent. Given a one-line description of a business,
your job is to produce a single-file landing page that looks great.

Process:
  1. Call TodoWrite with 4 todos: design, write index.html, sanity-check, open.
  2. Read skills/landing-page/SKILL.md for the design conventions.
  3. Write index.html to the current directory using Tailwind via CDN.
       - Five sections: hero, three highlights, hours, contact, footer
       - Use semantic HTML, mobile-first
       - Real-feeling copy specific to the business — no Lorem ipsum
       - Stock images via https://source.unsplash.com/featured/?keyword
  4. Run `python -c "from html.parser import HTMLParser; HTMLParser().feed(open('index.html').read()); print('OK')"`
     to sanity-check.
  5. Open the file: `open index.html` on macOS, `xdg-open index.html` on linux.
  6. Tell the user the file path.

Rules:
  - One file. No build step.
  - No animations longer than 200ms. No carousels.
  - Pick ONE primary color and ONE accent. Use neutrals for everything else.
"""


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")

    pitch = " ".join(sys.argv[1:]) or "a Brooklyn ramen shop called Sazae"
    prompt = f"build a landing page for: {pitch}"

    client = Anthropic()
    session = Session()
    agent_md = load_agent_md(Path.cwd())
    system = SYSTEM_OVERRIDE + ("\n\n# project context\n" + agent_md if agent_md else "")

    console.print(Panel.fit(
        f"[bold]microsite[/bold]  •  [dim]session {session.id}[/dim]\n"
        f"[dim]building: {pitch}[/dim]",
        border_style="dim"))

    agent_turn(client, session, system, prompt)


if __name__ == "__main__":
    main()
