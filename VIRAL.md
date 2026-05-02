# How to launch agent-101 (or any educational repo) for 100k stars

This is the playbook. Specific. Tactical. Ordered. Read it once, follow it once.

It pairs with [`docs/LAUNCH.md`](docs/LAUNCH.md) (which has the pre-drafted tweet/HN/Reddit copy). This file teaches the *strategy* behind the playbook.

---

## Part 1 — What actually drives 100k stars

Skip the cargo-culting. Three repos explain everything:

| Repo | Stars | What's true about all three |
|---|---|---|
| karpathy/nanoGPT | ~38k | Single author. Single voice. Manifesto, not framework. |
| karpathy/nanochat | ~52k | Three numbers in tweet 1 (`$100 / 4 hours / 8000 lines`). |
| OpenInterpreter/open-interpreter | ~63k | Demo video. `pip install`, one command, magic. |

The pattern is **(a) a single human's voice + (b) one viral hook number/visual + (c) a working artifact in <60 seconds**. Frameworks and corporate launches don't go viral the same way; you need a face, a number, and a thing.

For agent-101, the assets:
- **Face** — your GitHub profile, your handle, your manifesto tone in the README.
- **Number** — `18 chapters · ~3,000 LOC · 42 tests · 3 providers`. The leaderboard equivalent.
- **Working artifact** — `python agent.py "build me Tetris"` — runs in 60 seconds, produces a thing.

You already have all three. The launch is just *making people see them*.

---

## Part 2 — The 14 days before launch

**Days T-14 to T-7: build organic distribution.**

Don't launch cold. The week before the launch, post 1-2 substantive replies per day on the X accounts that share educational AI content. Substantive means: a useful technical comment, not a "great post!" reply. The 5 accounts to engage:

1. **@karpathy** — lineage justifies a *reply* mention later, never a tag in tweet 1
2. **@simonw** (Simon Willison) — actively shares educational AI repos on his blog
3. **@swyx** — Latent Space, agent-infra obsessive
4. **@hwchase17** (LangChain founder) — surprisingly amplifies "alternative" approaches
5. **@rasbt** (Sebastian Raschka) — built his audience on from-scratch educational content

You're not asking for anything yet. You're being a useful citizen of the timeline. When the launch happens, your name is recognizable.

**Days T-7 to T-1: dress rehearsal.**

- [ ] Read your README on a phone screen. Fix anything below the fold.
- [ ] Run `bash runs/speedrun.sh` end-to-end. Confirm everything passes.
- [ ] Run `python agent.py "build me Tetris..."` and screenshot the result.
- [ ] Generate `assets/launch.gif` with vhs.
- [ ] Build the 1280×640 OG image per `assets/README.md` and upload via repo Settings → Social preview.
- [ ] Pre-draft every tweet in the thread (don't compose live; copy from `docs/LAUNCH.md`).
- [ ] Pre-draft the HN title (no "Show HN").
- [ ] Pre-draft the r/LocalLLaMA, r/ClaudeAI, r/MachineLearning posts.
- [ ] Schedule 4 hours of uninterrupted time on launch day for replying to comments.

If any of these aren't done, **don't launch yet.** A missed item is a 50% reduction in your reach.

---

## Part 3 — Day 0 (Tuesday or Wednesday, 14:00–16:00 UTC)

The reason for Tuesday/Wednesday: HN front-page churn is fastest then. Avoid Monday (noisy with weekend backlog), Friday (dead by EU evening), weekends (dev twitter is off).

Time your minute-by-minute:

```
14:00 UTC  Post the Twitter thread (9 tweets, image on tweet 1, no link)
14:05 UTC  Reply to your own tweet 1 with the GitHub link
14:05 UTC  Submit to HN with the descriptive title (NOT "Show HN")
14:08 UTC  First-comment your own HN post: "Author here — context: ..."
14:10 UTC  Post to r/LocalLLaMA
14:15 UTC  STOP. No more posting. Watch HN.

14:15–18:00 UTC  Reply to every HN comment. Especially critical ones.
                 Concede where fair. Defend technical claims. Don't get into
                 LangChain flame wars.

After 18:00 UTC: rest. The first 4 hours determine whether you hit the front page.
```

What NOT to do on Day 0:
- Don't tag @karpathy / @AnthropicAI in tweet 1 (mute-bait — those accounts watch their @-mentions, see "look at me" posts, and ignore)
- Don't ask for HN upvotes anywhere (HN flags coordinated promotion)
- Don't cross-post to >1 subreddit on Day 0 (looks like spam)
- Don't use hashtags on Twitter (signals "marketing")
- Don't post on a Friday or weekend
- Don't get into LangChain flame wars in comments — concede where the framing might come across as hostile

---

## Part 4 — Day 1–7: the long tail

**Day 1 (Wednesday)**:
- LinkedIn post 13:00 UTC. Link in the *first comment*, not the post body — LinkedIn deprioritizes external links in posts. (Yes, this is dumb. Yes, it works.)
- r/ClaudeAI post (different sub from yesterday).
- Submit to TLDR AI (tldr.tech/ai), Ben's Bites, The Rundown AI.

**Day 2**: rest. Reply to issues + PRs that came in.

**Day 3**:
- Cross-post a long-form companion article to **dev.to only** (don't fragment to Hashnode/Medium — both are dying for dev content in 2026). Title: "Building an agent harness from scratch — a walkthrough of agent-101". Tags: `#ai #opensource #tutorial #python`.
- r/MachineLearning [P] post (strict rules — no marketing language).
- Discord posts: Anthropic Discord `#showcase`, MCP Discord, Latent Space `#projects`.

**Day 5 — the second wave**:
- Write a follow-up tweet thread: "What I learned launching agent-101" with star count, top issue, one technical insight from a contributor. Data-driven posts about your own launch outperform launch posts 2x. People love to see the post-mortem.

**Day 7**:
- Cold-pitch creators: Yannic Kilcher, Matthew Berman, AI Jason. Email format: short, repo link, *one paragraph* on why this is different from LangGraph tutorials.

**Week 2**:
- Ship v0.2 with the most-requested feature. Tweet about it.
- This is where 100k-stars repos diverge from 5k-stars repos. **One launch is not a strategy. The second post is the strategy.**
- nanoGPT got to 38k over *years*, with continuous attention from Karpathy. nanochat got to 52k in weeks because Karpathy already had 200k followers. Without an existing audience, plan for 5k by end of week 1, 10–25k by end of month 1 — IF you compound the second wave correctly.

---

## Part 5 — The numbers to track

The metrics that actually predict whether you hit 100k:

- **HN front-page time** (target: 4+ hours). If you don't hit the front page, the rest of the playbook delivers ~40% less.
- **First-day stars** (target: 1,000–3,000). Below 500 is a weak launch; above 3,000 is escape velocity.
- **Day-7 stars** (target: 5,000+). The slope from day 1 to day 7 predicts the long tail more than the day-1 spike.
- **Forks** (target: stars/10). Forks are the strongest signal that the repo is being used, not just bookmarked. If your stars/forks ratio is >20, your repo is being saved-for-later, not read.
- **Issue/PR count week 1** (target: 5+). Low issues + low PRs = the repo isn't being used. High issues = readers are engaging.
- **Cross-language ports** (target: 1 by end of week 4). The most viral signal. llm.c got llm.cpp / llm.zig / llm.rs / llm.metal precisely because Karpathy *invited* ports in the README. We do the same.

If your numbers are tracking, post them. Karpathy's "trending on HN so here it is :)" tweet is the canonical example — letting the audience see the momentum compounds the momentum.

---

## Part 6 — The compounding moves (week 2+)

These are what separate a 5k-stars launch from a 100k-stars trajectory.

**Companion video** — 5–10 minute YouTube walkthrough of agent.py, posted to your own channel. Karpathy's "Let's reproduce GPT-2" video drove a year-long second wave for nanoGPT. Plan to post yours by day 10.

**Leaderboard** — pre-populate at launch with a baseline entry; invite contributors to submit their own runs. nanochat's leaderboard converts passive stargazers into active contributors. For agent-101: a "minimum tokens to pass eval" leaderboard once `ch18_evals` is shipped.

**The "remix invitation"** — bake a "Notable ports" section into the README from day 0. Even seeded with a stub. llm.c shipped this; ports followed. Forks are an order of magnitude more valuable than stars for compounding.

**Manage criticism gracefully** — when someone posts a take on Twitter that's critical of the repo, *quote-retweet with a substantive reply.* Don't ignore. Don't dunk back. Engage on the merits. Critical engagement is a viral amplifier; defensive avoidance is not.

**Ship a chapter a week for 4 weeks post-launch.** From `docs/WISHLIST.md`: plan mode, vision, evals, reflection, prompt injection, computer use. Each ship gets its own tweet, its own discussion. This keeps the repo alive in feeds long after the launch spike fades.

---

## Part 7 — What to skip

Things that LOOK viral but reliably underperform:

- **Hashtags on X.** Signal "marketing." Depress engagement.
- **Show HN tag.** Karpathy never uses it. Never. Use a descriptive title instead.
- **Discord plugs in the README.** Educational repos converge. Go find readers; don't ask them to come to you.
- **"Star this repo" GIFs.** Microsoft and HuggingFace do this. They have 60k stars *despite* it. You're not Microsoft.
- **Long author bios.** Your face matters; your full CV doesn't.
- **Comparison tables that name competitors hostilely.** A comparison can be informative *without* picking a fight. We have one in the README that's careful about this — note the framing.

---

## Part 8 — When the spike happens, breathe

If the launch goes well, you will spend the first 48 hours in a euphoric haze of GitHub notifications. Two things to remember:

1. **Most stars come from people who haven't read the repo.** That's fine. Star counts are a discoverability signal, not a literacy signal. You'll know readers from forks, issues, and PRs.
2. **The work has just started.** Stars are the easy part. Now you have to *keep the repo alive* — answer issues, ship the wishlist, engage with ports, write the v0.2 changelog. Repos that compound do this for 6+ months. Repos that fade get one launch and silence.

---

## Adapt this to any educational repo

The playbook is repo-agnostic. The only repo-specific things are:

- The number triangle (yours: 18 chapters · 3,000 LOC · 42 tests · 3 providers)
- The 60-second demo (yours: `python agent.py "build me Tetris"`)
- The visuals (yours: chapter ladder, terminal screenshot, OG card)

Everything else applies to any technical educational repo: a from-scratch ML book, a tiny database implementation, a compiler tutorial, a graphics-from-scratch course.

The shape of viral is the shape of viral. The hook changes; the cadence doesn't.

---

*Last updated: 2026-05-02. If you adopt this playbook for your launch, [open an issue](https://github.com/KeWang0622/agent-zero-to-hero/issues) and tell me how it went — good or bad. Both data points are useful.*
