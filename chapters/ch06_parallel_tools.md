# Chapter 06 — Parallel Tool Calls 🐢

> **Claude can ask for three things at once. Run all three. Send all three back. In ONE user message. Or you'll teach it to stop being parallel.**

## 🐢 GuiGui says

This is the chapter with the silent foot-gun. The protocol *looks* fine even when you're doing it wrong. Latency just doubles. No error. You'll discover the bug a week later when your p95 blows up.

## The idea

Claude can emit MULTIPLE `tool_use` blocks in one assistant message. Run them in parallel. Bundle ALL `tool_result` blocks into ONE user message. Split them across messages → claude observes the pattern → stops issuing parallel calls. Silently.

## Show me the code

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as pool:
    futures = {b.id: pool.submit(dispatch, b.name, b.input)
               for b in r.content if b.type == "tool_use"}
    results = [{"type": "tool_result", "tool_use_id": tid, "content": fut.result()}
               for tid, fut in futures.items()]

msgs.append({"role": "user", "content": results})        # ALL results, ONE message
```

3 sequential 1-second tools = 3 seconds. 3 parallel = ~1 second. Same protocol — your code has to actually do it.

## ⚠️ Watch out for

**The serialization regression.** Splitting tool_results across multiple user messages teaches claude that parallel calls aren't useful. It silently stops emitting them. Track the parallel-call rate; alert if it drops mid-session.

## ✅ Summary

- Multiple tool_use in ONE assistant message → multiple tool_result in ONE user message.
- Run tools in parallel via ThreadPoolExecutor.
- Splitting tool_results across messages punishes parallel calls.

## 📝 Homework

```bash
python -m chapters.ch06_parallel_tools
```

1. Watch the wall clock. Should complete in ~1.1s, not 3.0s.
2. Modify the chapter to deliberately split results across messages. Run 5 times. Count how often claude emits parallel calls. Compare.
3. **Build a real demo:** weather agent that fetches 3 cities at once.

## 🚀 Next

[Chapter 07 — Errors](ch07_errors.md): tools fail. The loop must not.
