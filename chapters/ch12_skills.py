"""
chapter 12 — skills (markdown loaded on demand)

# A skill is a markdown file with YAML frontmatter. Claude reads the file
# only when it needs it. Don't put everything in the system prompt.

simon willison called this "maybe a bigger deal than MCP." the idea is:

  the system prompt should be SHORT. it should be claude's persona and a
  CATALOG of what's available. the actual procedural knowledge lives in
  separate files claude can read on demand.

so:
  - SYSTEM PROMPT (always loaded, ~500 tokens):
      "you have skills: 'invoice-design', 'sql-debugging', ...
       call read_skill(name) to load one when needed."

  - skills/invoice-design/SKILL.md (loaded when claude calls read_skill):
      ---
      name: invoice-design
      description: How to design an invoice. Use when user asks for an invoice.
      ---
      [3000 tokens of detailed instructions]

claude code, openclaw, and now the API itself work this way. the trick is
PROGRESSIVE DISCLOSURE: pay attention budget only when relevant.

what you'll learn:
  - the SKILL.md format (yaml frontmatter + markdown body)
  - building the catalog (a list of name+description for the system prompt)
  - the read_skill meta-tool (returns the markdown body)
  - composing skills with regular tools

run:
  python -m chapters.ch12_skills

next: ch13 — the MCP wire format (json-rpc over stdio, from scratch).
"""

import os
import sys
from pathlib import Path

from anthropic import Anthropic


client = Anthropic()
MODEL = "claude-sonnet-4-5"
SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


# --- skills loader -------------------------------------------------------

def parse_skill_md(path: Path) -> dict:
    """Parse a SKILL.md: yaml frontmatter + markdown body."""
    text = path.read_text()
    # YAML frontmatter parsing without a yaml dep — we just need name + desc.
    if not text.startswith("---\n"):
        return {"name": path.parent.name, "description": "(no frontmatter)", "body": text}
    end = text.index("\n---\n", 4)
    fm = text[4:end]
    body = text[end + len("\n---\n"):]
    meta = {}
    for line in fm.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip("'\"")
    meta["body"] = body
    return meta


def load_catalog() -> dict[str, dict]:
    """Discover all skills/<name>/SKILL.md."""
    catalog = {}
    for skill_md in SKILLS_DIR.glob("*/SKILL.md"):
        meta = parse_skill_md(skill_md)
        catalog[meta["name"]] = meta
    return catalog


def build_skills_prompt(catalog: dict) -> str:
    """Just the catalog (name + 1-line desc). The body is NOT in the system prompt."""
    if not catalog:
        return ""
    lines = ["You have access to skills (read on demand):"]
    for s in catalog.values():
        lines.append(f"  - {s['name']}: {s['description']}")
    lines.append("Call read_skill(name) to load a skill's body when needed.")
    return "\n".join(lines)


# --- agent loop with skill loading ---------------------------------------

def agent_loop(prompt: str):
    catalog = load_catalog()
    system = (
        "You are agent-101 with access to skills. Use read_skill() before "
        "starting any task that matches a skill description.\n\n"
        + build_skills_prompt(catalog)
    )

    tools = [
        {"name": "read_skill",
         "description": "Load a skill's markdown body by name.",
         "input_schema": {"type": "object",
                          "properties": {"name": {"type": "string"}},
                          "required": ["name"]}},
        {"name": "echo",
         "description": "Echo a string (proves the skill was applied).",
         "input_schema": {"type": "object",
                          "properties": {"text": {"type": "string"}},
                          "required": ["text"]}},
    ]

    msgs = [{"role": "user", "content": prompt}]

    for turn in range(15):
        r = client.messages.create(model=MODEL, max_tokens=2048,
                                   system=system, tools=tools, messages=msgs)
        msgs.append({"role": "assistant", "content": r.content})

        for b in r.content:
            if b.type == "text" and b.text.strip():
                print(f"\nclaude> {b.text}")

        if r.stop_reason != "tool_use":
            return

        results = []
        for b in r.content:
            if b.type == "tool_use":
                if b.name == "read_skill":
                    name = b.input["name"]
                    if name in catalog:
                        body = catalog[name]["body"]
                        print(f"  [skill loaded: {name} ({len(body)} chars)]")
                        results.append({"type": "tool_result",
                                        "tool_use_id": b.id, "content": body})
                    else:
                        results.append({"type": "tool_result",
                                        "tool_use_id": b.id,
                                        "content": f"unknown skill: {name}",
                                        "is_error": True})
                elif b.name == "echo":
                    print(f"  [echo: {b.input['text'][:200]}]")
                    results.append({"type": "tool_result",
                                    "tool_use_id": b.id,
                                    "content": "echoed: " + b.input["text"]})
        msgs.append({"role": "user", "content": results})


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY first")
    agent_loop("write me a haiku in the style described in the haiku-master skill, "
               "then echo it.")
