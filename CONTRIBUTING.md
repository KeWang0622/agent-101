# Contributing

agent-zero-to-hero is an educational repo. Its goal is to teach how an agent harness works, in 18 numbered files of Python you can read on a flight. Contributions that *advance that goal* are welcome. Contributions that turn it into a framework are not.

## Welcome contributions

- **Bug fixes.** If a chapter or `agent.py` has a real bug, please open an issue with reproduction. Or send a PR.
- **Clarification edits to chapter prose.** If a docstring or `CONCEPT.md` is unclear, you understand the bar — make it clearer. Keep the planted misconception → wrong version → right version → named failure → try-this structure.
- **Ports to other languages.** Open a PR adding your link to the README's "Notable ports" table. Naming convention: `agent-zero-to-hero-go`, `agent-zero-to-hero-rust`, `agent-zero-to-hero-ts`.
- **Additional tests.** Especially provider-edge-case tests against mocks. Tests that need API keys are fine if they're tagged so they skip in CI.
- **New chapters** that cover ONE missing concept. The bar: the concept must show up *every week* in real agent-builders' GitHub issues. See `docs/WISHLIST.md` for the chapters we've prioritized.

## Not welcome

- Frameworks. No `pip install agent-zero-to-hero`. No factory classes. No abstract base classes for tools.
- Configurability for its own sake. Karpathy's manifesto: *"not an exhaustively configurable framework... single, cohesive, minimal, readable, hackable, maximally-forkable strong baseline."*
- Multi-paragraph docstrings explaining what `def add(a, b)` does.
- Architecture diagrams that don't fit in a terminal at 80 cols.

## How to send a PR

1. Fork.
2. `pip install -e ".[test]"` and `pytest tests/` — get a green bar.
3. Make the change.
4. Run the tests again.
5. If you added a chapter, also add a corresponding test file.
6. Open the PR. Describe the *misconception your change resolves* in the description.

## House style

- Lowercase H2 / H3 headings (matches Karpathy's style).
- Comments explain **why**, not what. Never narrate code.
- Function bodies under ~30 lines. Long blocks split into small functions.
- No type hints in chapter code (clarity over rigor — this is a textbook). Type hints fine in `agent.py`.
- Anthropic-canonical vocabulary: `tool_use`, `tool_result`, `stop_reason`, `messages`, `system`, `compaction`, `skills`, `MCP`. Don't invent new terms.

## License

By contributing, you agree your contribution is MIT-licensed.
