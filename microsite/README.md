# microsite — the capstone

The 30-second demo. Build a landing page from a one-line prompt using the
`agent.py` you wrote across chapters 1–17.

## Run

```bash
cd microsite
python build_site.py "a Brooklyn ramen shop called Sazae"
# → writes index.html, opens it
```

You'll watch the agent:

1. Plan with TodoWrite (4 steps)
2. Read the `landing-page` skill
3. Write `index.html` (Tailwind via CDN, 5 sections, real photos via Unsplash)
4. Sanity-check the HTML
5. Open it in your default browser

Then iterate:

```bash
python ../agent.py
> the menu cards should be bigger and the palette warmer
```

The agent edits `index.html` in place. Reload the browser to see changes.

## Why this is the capstone

- It uses every primitive: loop, tools, parallel calls, sessions, skills, error recovery.
- It produces a screenshot — share-ready output.
- It's not the website-cloner. You're creating from a description, not copying a URL.
- The narrative arc: "you built `agent.py`, now use it to ship something real."

## Try these prompts

```
"a coffee shop in Tokyo called Hayashi"
"a portfolio for a freelance illustrator named Mira"
"a landing page for an indie game called 'Echo' — sci-fi, dark mode"
"a SaaS for dog walkers in Brooklyn called Walkie"
```
