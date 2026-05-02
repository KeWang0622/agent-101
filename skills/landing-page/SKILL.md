---
name: landing-page
description: How to design a landing page. Use when the user asks to build a website or marketing page.
---

# Landing page — the canonical structure

A landing page that converts has five sections, in order:

1. **Hero** — one-sentence promise + visual + ONE primary CTA.
2. **Three highlights** — three benefits in three cards. No more.
3. **Hours / details** — practical info above the fold of the second screen.
4. **Map / contact** — embedded iframe or link.
5. **Footer** — minimal: copyright, social links.

## Tech rules (the engineering parts)

- **One file.** `index.html` with inline `<style>` and `<script>`. No build step.
- **Tailwind via CDN** — `<script src="https://cdn.tailwindcss.com"></script>`. Don't pull npm.
- **Stock photos via Unsplash source URLs** — `https://source.unsplash.com/featured/?keyword`.
- **Mobile-first.** Test at 375px width.
- **No animations longer than 200ms.** No carousels. No popups.

## Color guidance

- Pick ONE primary color and ONE accent. Use neutrals for the rest.
- For warm businesses (food, hospitality): orange/red primary, cream neutral.
- For tech: blue/indigo primary, slate neutral.
- Never use pure black on pure white — soften both.

## Procedure

When asked to build a landing page:

1. Identify the business type from the prompt.
2. Pick a color palette using the guidance above.
3. Write `index.html` with the five sections.
4. Use real-feeling copy (no "Lorem ipsum"). Make it specific to the prompt.
5. After writing, use the `bash` tool to `open index.html` (macOS) or `xdg-open index.html` (Linux).
6. If the user asks for changes, use Edit to make targeted changes — don't rewrite.
