# Chapter 13 — MCP Demystified

> **MCP is "USB-C for AI" if you're selling it. From the wire, it's three things:
> a child process, line-delimited JSON-RPC 2.0, three method calls.**

## The hook

When Anthropic announced MCP, half the engineering Twitter discourse was "this is the most important thing since function calling" and the other half was "what is it actually." Both were right — it IS important, AND nobody can tell you what it actually is. The marketing material talks about "the protocol that lets AI connect to anything" and shows a USB-C cable. After three months of writing tools for Claude Code I still didn't know what bytes flowed through the cable.

This chapter answers that. We spawn an MCP server (the calculator one in `mcp_servers/`), send three raw JSON-RPC messages over its stdin/stdout, and print what comes back. No SDK. No abstractions. Just bytes.

## What you already know

From `ch04_one_tool.py`: a tool is `{name, description, input_schema}` plus a function. You declare it locally and Claude routes `tool_use` blocks to your dispatcher. MCP doesn't change that — MCP just lets the dispatcher live in a *different process*.

## The wrong version

The naive guess: MCP is a complicated wire protocol with a registry server, capability negotiation, version brokering, and a binary framing format. It must require a library, special tools, maybe a daemon.

It's none of that. The "protocol" is JSON-RPC 2.0 — the same wire format the LSP (Language Server Protocol) uses, the same every editor uses to talk to clangd or rust-analyzer. The "framing" is one JSON object per line over stdin/stdout. The "registry" is a config file. There are exactly **three method calls** you ever need: `initialize`, `tools/list`, `tools/call`.

## The right version

```
   YOUR CLIENT                          MCP SERVER (child process)
   ┌──────────────┐                     ┌──────────────────────┐
   │              │  1. initialize      │ {protocolVersion,    │
   │  (this file) │ ──────────────────▶ │  serverInfo,         │
   │              │ ◀────────────────── │  capabilities}       │
   │              │                     │                      │
   │              │  notifications/initialized                 │
   │              │ ──────────────────▶ │                      │
   │              │                     │                      │
   │              │  2. tools/list      │ {tools:[             │
   │   stdin  ──▶ │ ──────────────────▶ │  {name, description, │
   │   stdout ◀── │ ◀────────────────── │   input_schema}, …]} │
   │              │                     │                      │
   │              │  3. tools/call      │ {content:[           │
   │              │ ──────────────────▶ │  {type:"text",       │
   │              │ ◀────────────────── │   text:"42"}]}       │
   └──────────────┘                     └──────────────────────┘
       line-delimited JSON-RPC 2.0 over pipes. that's it.
```

The three calls in detail:

1. **`initialize`** — handshake. You send your protocol version and clientInfo; you get back the server's capabilities (does it support tools? resources? prompts?). The spec then requires a `notifications/initialized` notification (no response expected) before any other call.

2. **`tools/list`** — *"what can you do?"* Returns an array of tool descriptors with `name`, `description`, `inputSchema`. Cache these locally; convert each into Anthropic's tool format (rename `inputSchema` → `input_schema`, namespace as `mcp__<server>__<tool>`).

3. **`tools/call`** — *"run this one with these args."* Returns `{content: [...]}` — note the *content blocks*, mirroring Anthropic's tool result shape. If the call failed, the server sets `isError: true`.

After this chapter you will never wonder what MCP "is" again.

## What could go wrong

**The orphan child process.** Symptom: you run `python -m chapters.ch13_mcp_wire`, the demo prints fine, but `ps aux | grep python` shows a zombie `calculator_server.py` still running. Now you're at 17 zombie servers and your Mac fan is at full speed. Cause: forgetting to call `proc.stdin.close()` and `proc.wait()` when the client exits.

Fix: always wrap MCP clients in `try/finally` and call `mcp.close()` in the finally block. `ch13_mcp_wire.py` does this at line 83. In production, also handle `SIGINT` to clean up children when the user hits Ctrl-C.

## Try this

```bash
python -m chapters.ch13_mcp_wire
```

The output prints every byte of the JSON-RPC exchange — three calls, three responses. Things to notice:

1. The **`id` field** on requests. Each request gets a numeric id; responses echo it back. If your client is sending many requests in flight (which we're not), the id is what pairs them up.
2. The **shape of `tools/call` results**. They're arrays of typed content blocks — same family as Anthropic's response content blocks. This is on purpose. MCP was designed to drop into Anthropic's existing protocol with zero impedance.
3. Try point Claude Desktop at this same server. Open `~/Library/Application Support/Claude/claude_desktop_config.json` and add an entry pointing at `mcp_servers/calculator_server.py`. Restart Claude Desktop. Ask it "what is 17 \* 23?" and watch your server's stdout.

## When NOT to use this

If your tools are local Python functions, you don't need MCP — declare them inline as in `ch04_one_tool.py`. MCP is for *cross-process* boundaries: your tools live in another language (Go, Rust, TypeScript), or another machine, or you want one tool server to be sharable across multiple agent instances.

## Where this shows up in agent.py

`agent.py` doesn't use MCP directly — its tools are local Python. To wire MCP servers into `agent.py`, the pattern from `ch14_mcp_agent.py` is the answer: spawn the server at startup, list its tools, prepend them to your TOOLS list with the `mcp__server__name` prefix, and route `tool_use` calls by detecting that prefix.

## Going deeper

- [The MCP specification](https://spec.modelcontextprotocol.io) — readable; ~30 pages of JSON-RPC schema
- [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) — what we're NOT using; FastMCP hides the wire
- [Claude Desktop MCP config docs](https://modelcontextprotocol.io/quickstart/user) — wire your server into the desktop app and watch it call your code
