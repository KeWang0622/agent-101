# Chapter 05 — THE LOOP 🐢

<p align="center">
  <img src="../assets/ch05-illustration.png" alt="The agent loop" width="100%">
</p>

> **The thing the model can't do is run code. The thing you can't do is think. An agent loop is just `while True` of one talking to the other.**

## 🐢 GuiGui says

This is the chapter the entire course pivots on. Everything before it built up to one insight. Everything after it adds layers around it. **By the end of this chapter you can write Cursor / Claude Code / Devin from a blank file.**

## The idea

Chapter 04 was a *two-call protocol*: ask, run tool, send result, get answer. **One round-trip.** That works for one-step problems. It breaks when Claude needs information it doesn't yet have:

> *"What's the biggest Python file in chapters/?"*

Claude's first call is `glob`. Then `wc -l`. Then "the biggest is X." **Three round-trips minimum.** The fix is one keyword: `while`. Wrap chapter 4's protocol in a loop, and the agent can call any number of tools, in any order, until it has enough information to answer.

## The 6 lines (annotated)

```python
def agent_loop(prompt: str):
    msgs = [{"role": "user", "content": prompt}]              # ① the only state

    for turn in range(MAX_TURNS):                             # ② cap it. always.
        r = client.messages.create(                           # ③ the one API call
            model=M, tools=TOOLS, messages=msgs, max_tokens=2048
        )
        msgs.append({"role": "assistant", "content": r.content})  # ④ persist reply

        if r.stop_reason != "tool_use":                       # ⑤ exit when done
            return r

        msgs.append({"role": "user", "content": [             # ⑥ run + append + loop
            {"type": "tool_result", "tool_use_id": b.id,
             "content": dispatch(b.name, b.input)}
            for b in r.content if b.type == "tool_use"
        ]})

    raise RuntimeError(f"hit MAX_TURNS={MAX_TURNS}")
```

That's it. That's the entire loop. Everything else (sessions, compaction, MCP, skills, multi-provider) is **layers around these six lines.**

---

## 🤔 But how does Claude *know* what to do?

This is the question the rest of this chapter answers. It's the deepest question of the course.

### Short answer: it doesn't "know" — it predicts

The model has **no orchestrator, no planner, no separate reasoning module**. When you call the API, three things go into one forward pass: `system` prompt + `messages` + `tools`. The model emits its reply by predicting the most likely next text — token by token. That reply happens to contain a `tool_use` block because, given the tool *descriptions* and the question, the most likely text is something like *"I'll list the files first"* + a structured request to do exactly that.

There is no plan. There's a learned pattern from training: humans break down problems, so the model imitates that pattern when it sees a similar setup.

### Decomposition lives in three places — none of them in your code

| Source | What it does | Lever |
|---|---|---|
| **Training data** | Claude was fine-tuned on agent traces (ReAct-style). Decomposition is built in. | None — already there |
| **Tool descriptions** | Each `description` shifts which tool gets picked. *"Find files matching a glob pattern"* matches the question better than *"Run a bash command"*. | **Rewrite descriptions** until the right tool is chosen. Highest leverage. |
| **System prompt** | Rules like *"Gather context first via Glob/Grep before acting"* convert probabilistic decomposition into reliable decomposition. | **Add explicit workflow rules** — see [ch08](ch08_system_prompts.md). |

When your agent does something stupid, the bug is almost always in one of these three. **Most "agent prompt engineering" is rewriting tool descriptions until the model reliably picks the right tool.** You'll spend more time on this than on the loop itself.

### See it for yourself: the "thinking out loud" trick

A single assistant turn often contains BOTH text and tool_use blocks — generated together in one inference. Print `r.content` after a turn:

```python
r.content = [
    TextBlock(text="I'll start by listing the files."),    # ← reasoning
    ToolUseBlock(name="glob", input={"pattern": "chapters/*.py"})
]
```

That text isn't separate "thinking" — it's literal output, generated alongside the tool call. **Read it. Print it. Use it as a debugging hook to see the model's mid-task reasoning.**

---

## 🔄 The ReAct cycle: how multi-step actually works

Each iteration of your `for turn in range(MAX_TURNS)` is one round of the **ReAct cycle** (Reason → Act → Observe). Claude was trained on this pattern explicitly:

```
turn 0:  REASON   "I'll list the files first."     ← text block
         ACT      glob(pattern="chapters/*.py")    ← tool_use block
              ───────────────────────────────────
your code:  YOU run glob, append the result
              ───────────────────────────────────
turn 1:  OBSERVE  reads tool_result in messages    ← happens implicitly
         REASON   "Now I need their line counts."  ← text block
         ACT      bash(cmd="wc -l chapters/*.py")  ← tool_use block
              ───────────────────────────────────
your code:  YOU run bash, append the result
              ───────────────────────────────────
turn 2:  OBSERVE  reads the bash output
         REASON   "ch17 has 258 lines."
         ANSWER   stop_reason = "end_turn"          ← exits loop
```

Three turns. Each turn is one inference. **The "Observe" step doesn't take its own turn** — it happens at the start of the *next* turn, when claude reads the tool_result that's now in messages.

### Why this is *reactive*, not *planned*

In turn 0, Claude said *"I'll list the files first."* — that looks like a plan. **It isn't.** It's just predicted text, the way *"once upon a time"* is predicted text after a fairy-tale prompt. By turn 1, that "plan" is just old context in the messages array. Claude rereads it and roughly follows it, but it could deviate based on what `glob` returned. If `glob` had returned ONE file, claude would have skipped `wc -l` and answered directly.

**The plan isn't a commitment. It's just a prediction the model can later abandon.**

### So the model is reactive by default. Is that good or bad?

For most tasks: **good enough**. Each turn gets to update its plan based on real observations. That's robust to surprise — if a file is missing, claude doesn't blindly continue.

For long, structured tasks (>5 steps): **fragile**. The model can lose the thread, redo work it already did, or skip steps that "felt obvious" mid-task. To get reliable multi-step behavior, you need to add **explicit planning**.

---

## 📋 When you DO want explicit planning: TodoWrite

Three escalating techniques, ordered by reliability:

### 1. System prompt rule (soft)
```python
SYSTEM = "For tasks with more than 2 steps, write a numbered plan first, then execute it."
```
Shifts the distribution toward decomposition. ~80% reliable. Cheap.

### 2. TodoWrite tool (hard) — Claude Code's pattern
Add a tool whose only job is to **materialize the plan as a tool call**:

```python
{"name": "TodoWrite",
 "description": "Track a multi-step plan. Call FIRST when starting any task with >2 steps.",
 "input_schema": {
     "type": "object",
     "properties": {"todos": {"type": "array",
         "items": {"type": "object",
             "properties": {
                 "content": {"type": "string"},
                 "status":  {"enum": ["pending", "in_progress", "completed"]},
             }}}},
     "required": ["todos"]}}
```

Real trace using this tool:
```
turn 0 → TodoWrite([
  {content: "list python files in chapters/", status: "in_progress"},
  {content: "count lines per file",            status: "pending"},
  {content: "report the longest one",          status: "pending"},
])
turn 1 → glob(...)
turn 2 → TodoWrite([... step 1 completed, step 2 in_progress ...])
turn 3 → bash(wc -l ...)
turn 4 → TodoWrite([... all completed ...]) + final answer
```

The plan is now **observable, debuggable, and self-correcting**. If something breaks mid-run, you can read the todos to see where claude was. Drop in error rates of ~30% on real coding tasks.

`agent.py` ships TodoWrite — see line 154.

### 3. Plan mode (hardest) — separate two-phase agent
A *separate* read-only loop produces a plan document. A human approves. A *second* loop with write access executes it. Out of scope for this chapter; see Claude Code's plan-mode UI for the canonical implementation.

---

## ⚠️ Watch out for

**The runaway loop.** Without a cap, a buggy tool that returns "try again" can cost $40 in an hour. **Always `for turn in range(MAX_TURNS)`, never bare `while True`.**

**Goldfish agents.** Re-creating `msgs = []` inside the loop = fresh start every turn. Build it ONCE outside the loop.

**Skipping `messages.append(r.content)`.** The next turn's call will get a role-alternation 400 because there's no assistant message between the user's prompt and the tool_results.

## ✅ Summary

- Agent = `while True { call → dispatch → continue }`. Six lines.
- Decomposition is **predicted, not planned** — driven by training, tool descriptions, and the system prompt.
- Each turn = one ReAct cycle (Reason + Act, then Observe at the start of the next turn).
- The model is **reactive** by default. For reliable multi-step planning, add a `TodoWrite` tool.
- A turn cap is non-negotiable.

## 📝 Homework

```bash
python -m chapters.ch05_the_loop "what's the biggest python file in chapters/?"
```

1. Count turns. Should be 2-4. Add `print(f"=== turn {turn} ===")` and observe the ReAct cycle.
2. Print `r.content` after each call. Read the text-before-tool_use reasoning.
3. **Decomposition test:** edit `chapters/ch05_the_loop.py` to corrupt the `glob` description (change it to `"List files (rarely useful)"`). Re-run. Watch claude either skip glob entirely or pick bash instead. Reset and verify glob comes back.
4. **Planning test:** add a `TodoWrite` tool to ch05's TOOLS list. Run a 5-step task. Compare turn count vs without TodoWrite.
5. **Synthesis (100 words):** Why is the model reactive by default — and when is that *not* what you want?

## Where this shows up in agent.py

`agent.py` — the `agent_turn` function (around line 629) is the same six lines, plus streaming, plus retries, plus permissions, plus session writes. The `TodoWrite` tool is registered in the default TOOLS list (line 154) and the system prompt explicitly tells claude to use it for multi-step work (lines 526-540).

## 📚 References

**Foundational papers**
- [Yao et al. — ReAct: Synergizing Reasoning and Acting in Language Models (2022)](https://arxiv.org/abs/2210.03629) — the paper. Read it.
- [Shinn et al. — Reflexion (2023)](https://arxiv.org/abs/2303.11366) — adding self-critique to the ReAct loop
- [Wei et al. — Chain-of-Thought Prompting (2022)](https://arxiv.org/abs/2201.11903) — why "thinking out loud" works

**Anthropic's frame**
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — the canonical taxonomy of agent patterns
- [Anthropic — How we built Claude Code's multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — production lessons

**Karpathy lineage**
- [Karpathy — Software 3.0 (2025 talk)](https://www.youtube.com/watch?v=LCEmiRjPEtQ) — the agent loop as a primitive
- [karpathy/nanoGPT](https://github.com/karpathy/nanoGPT) — the literary template this course follows

**Production references**
- [openclaw](https://github.com/openclaw/openclaw) — open clone of Claude Code; read its `src/agents/pi-embedded-runner/run.ts`
- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) — 12-session course covering the same primitives

## 🚀 Next

[Chapter 06 — Parallel tools](ch06_parallel_tools.md): claude can ask for three things at once. The single-user-message rule.
