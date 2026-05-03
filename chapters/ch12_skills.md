# Chapter 12 — Skills: Markdown Loaded On Demand 🐢

> **A skill is a markdown file with YAML frontmatter. Claude reads it only when needed. Don't put everything in the system prompt.**

## 🐢 GuiGui says

Simon Willison called this "maybe a bigger deal than MCP." The system prompt should be SHORT. It should contain claude's persona AND a CATALOG of available skills. Procedural knowledge lives in separate files, loaded on-demand. **Progressive disclosure.**

## The shape

```
skills/
  haiku-master/SKILL.md       ← 200 lines of how to write haiku
  invoice-design/SKILL.md     ← 500 lines of design rules
  sql-debugging/SKILL.md      ← 800 lines of pitfalls
```

Each `SKILL.md` is YAML frontmatter (name + description) + markdown body.

## Show me the code

```python
# parse a skill on disk
def parse_skill(path):
    text = path.read_text()
    # frontmatter between --- markers
    fm, body = text.split("---", 2)[1:3]
    meta = {l.split(":", 1)[0].strip(): l.split(":", 1)[1].strip()
            for l in fm.strip().splitlines() if ":" in l}
    return {**meta, "body": body}

# system prompt = catalog (NOT bodies)
catalog = "\n".join(f"  - {s['name']}: {s['description']}" for s in skills)
SYSTEM = f"You have skills:\n{catalog}\nCall read_skill(name) to load one."

# meta-tool the model can call
TOOLS = [{"name": "read_skill",
          "description": "Load a skill body by name.",
          "input_schema": {"type": "object",
                          "properties": {"name": {"type": "string"}},
                          "required": ["name"]}}]
```

## ⚠️ Watch out for

**The catalog overload.** 50 skills with vague descriptions → claude doesn't know which to load → calls 5 in sequence "to check." Fix: each `description` makes the load decision OBVIOUS. "Helps with code" is bad. "Debug Django N+1 queries — use when user mentions slow page loads" is good.

## ✅ Summary

- Skills = on-demand context, not eager system-prompt bloat.
- Catalog (name + 1-line description) goes in system. Bodies don't.
- One meta-tool `read_skill(name)` returns the body.

## 📝 Homework

```bash
python -m chapters.ch12_skills
```

1. Add a `weather-formatter` skill at `skills/weather-formatter/SKILL.md`. Verify discovery.
2. Compute: a 5-skill agent's system prompt cost (catalog only) vs eager-loaded (all bodies). 10×? 50×?
3. Add `read_skill` to `agent.py`. Make it skill-aware.

## 📚 References

- [Anthropic — Equipping agents with Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — the official launch post
- [Simon Willison — Claude Skills are maybe a bigger deal than MCP](https://simonwillison.net/2024/Oct/16/claude-skills/) — why this chapter exists
- [Anthropic — Claude Code skills directory](https://docs.anthropic.com/en/docs/claude-code/skills) — the canonical SKILL.md format
- [openclaw — `skills/` directory](https://github.com/openclaw/openclaw/tree/main/skills) — production examples

## 🚀 Next

[Chapter 13 — MCP demystified](ch13_mcp_wire.md): tools across process boundaries.
