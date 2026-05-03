# Chapter 14 — Wire MCP Into the Agent Loop 🐢

> **An MCP tool is just a remote function. Convert its schema. Route `tool_use` calls back as `tools/call`. Claude can't tell the difference.**

## 🐢 GuiGui says

[Chapter 13](ch13_mcp_wire.md) showed the wire. Now we make MCP tools indistinguishable from local tools — same dispatch loop, two field renames, one prefix.

## The translation

| Anthropic | MCP |
|---|---|
| `name` | `name` |
| `description` | `description` |
| `input_schema` | `inputSchema` |

Two field renames. Plus a `mcp__<server>__<tool>` prefix to disambiguate.

## Show me the code

```python
def to_anthropic_tool(server_id, mcp_tool):
    return {
        "name": f"mcp__{server_id}__{mcp_tool['name']}",
        "description": f"[{server_id}] {mcp_tool['description']}",
        "input_schema": mcp_tool["inputSchema"],
    }

# in the loop's dispatch:
if b.name.startswith("mcp__"):
    _, server_id, tool_name = b.name.split("__", 2)
    out = mcp_clients[server_id].call_tool(tool_name, b.input)
else:
    out = local_handlers[b.name](**b.input)
```

That's it. Local + MCP behind one dispatch.

## ⚠️ Watch out for

**The blocked stdin.** If the MCP server crashes (or floods stderr you're not reading), its stdout goes silent and your `readline()` blocks forever. Always: timeout on read, SIGTERM on hang.

## ✅ Summary

- MCP tool → Anthropic tool: 2 field renames + namespace prefix.
- Routing: prefix `mcp__` → MCP client; otherwise local.
- Same dispatch loop. Claude doesn't know the difference.

## 📝 Homework

```bash
python -m chapters.ch14_mcp_agent "what is (17 * 23) + 1234?"
```

1. Watch the JSON-RPC trace + the model's final answer.
2. Connect TWO MCP servers (calculator + a custom weather server you write).
3. Add MCP support to `agent.py` (~50 LOC). Send a PR.

## 📚 References

- [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) — what we're NOT using; FastMCP hides the wire
- [MCP — tool integration patterns](https://modelcontextprotocol.io/docs/concepts/tools) — official guide
- [LangChain — MCP integrations](https://python.langchain.com/docs/integrations/tools/mcp/) — alternative client implementation worth comparing
- [`mcp__` namespace convention in Claude Code](https://docs.anthropic.com/en/docs/claude-code/mcp) — where the prefix originated

## 🚀 Next

[Chapter 15 — Streaming text](ch15_streaming_text.md): make the tokens appear one at a time.
