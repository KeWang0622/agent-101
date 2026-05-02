# Common confusions

The three questions every reader asks. Answered in one sentence each.

### Q: Why not LangChain / LangGraph / CrewAI / AutoGen?

Those are frameworks; this is a textbook. Frameworks tell you *what to type*; agent-101 tells you *what's underneath*. If you understand chapter 5, you understand what every agent framework on Earth is wrapping. Then if you choose to use one, you'll know exactly when it's helping and when it's hiding the bug.

### Q: Why Anthropic and not OpenAI / Gemini in the main chapters?

Anthropic's wire format is the cleanest expression of agent concepts: `tool_use` and `tool_result` are typed content blocks, `input` is a parsed object (no JSON-string detour), there's exactly one shape per concept. OpenAI has Chat Completions *and* Responses (two formats for the same thing). Gemini doesn't have a dedicated tool-use stop reason. **Chapter 17 is the adapter** that makes the same agent run on all three. Once you understand the Anthropic loop, the others are 50-line ports.

### Q: Is this production-ready?

No, and that's the point. This is a **textbook** — read it, copy it, throw it away. After you understand it, go read [openclaw](https://github.com/openclaw/openclaw) (production CLI) or [Anthropic's claude-code](https://github.com/anthropics/claude-code) source. Or build your own production thing — you'll know what you need.

### Q: How long does it take to get through?

If you read every chapter and run every demo: ~5 hours. If you skip the demos and just read: ~2 hours. If you're already comfortable with the Anthropic SDK: ~45 minutes for the parts you don't already know.

### Q: I don't have an API key. Can I still use this?

Yes. `pytest tests/` passes 18 tests with no API key. The MCP tests spawn a real subprocess and exchange real JSON-RPC. The multi-provider tests verify the foot-guns. You can confirm everything works before you sign up.
