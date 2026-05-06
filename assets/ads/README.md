# Launch ads

Four short (17–23 s) talking-head ads for posting to X, Bluesky, LinkedIn, Reddit comments, Discord, etc. GuiGui avatar lipsynced to Ke's cloned voice. Hormozi-style word-by-word yellow-highlight captions burned in for muted autoplay.

| File | Hook | Duration | Best for |
|---|---|---|---|
| [`ad1-the-loop.mp4`](ad1-the-loop.mp4) | "Six lines. That's the entire agent loop." | ~17 s | Universal — broadest appeal, lowest barrier to share |
| [`ad2-vs-frameworks.mp4`](ad2-vs-frameworks.mp4) | "LangChain is 120K lines. Mine is 4,500." | ~22 s | Polarizing — gets QTs, framework debates |
| [`ad3-mcp-demystified.mp4`](ad3-mcp-demystified.mp4) | "MCP isn't magic. It's JSON-RPC over stdio." | ~22 s | The curious-but-confused crowd |
| [`ad4-capstone.mp4`](ad4-capstone.mp4) | "YOUR agent ships a real website from one prompt." | ~20 s | Show-don't-tell — converts watchers to clickers |

## How to use

**Don't post all 4 at once.** Stagger over Days 0–7:

- **Day 0 (HN launch day, T+5 min)** → `ad1-the-loop.mp4` (attached to tweet 1 of the launch thread instead of the static loop image)
- **Day 1 morning** → `ad4-capstone.mp4` (the "show don't tell" follow-up)
- **Day 3** → `ad2-vs-frameworks.mp4` with the launch retrospective thread
- **Day 5 (Karpathy-bait standalone tweet)** → `ad3-mcp-demystified.mp4`

This keeps the algorithm fed with fresh video without burning all the assets in one feed-position.

## Why portrait (3:4) instead of vertical (9:16)

Pika lipsync output is portrait around the avatar headshot. 3:4 plays full-frame on X / Bluesky / LinkedIn (which all crop 9:16 to 3:4 anyway), and on Reels / Shorts / TikTok the platform letterboxes acceptably. One asset, 5 platforms.

## Re-render

Each ad is built from a 3-step pipeline against the Pika MCP:

1. `generate_speech` (minimax-tts) with the persona's `identity_voice_id`
2. `generate_lipsync` (pika provider — fast, parrot a2v) with `identity_avatar_url` + the audio
3. `add_captions` (style: `hormozi`)

Total wall-clock: ~5–8 minutes per ad on the pika provider. Edit the scripts inside `scripts/build_ads.py` if you change the angles.
