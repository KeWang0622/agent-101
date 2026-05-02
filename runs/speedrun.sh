#!/usr/bin/env bash
# runs/speedrun.sh — execute every chapter in order. ~10 minutes.
#
# usage:
#   export ANTHROPIC_API_KEY=sk-ant-...
#   bash runs/speedrun.sh
#
# costs ~$0.50 in API calls on claude sonnet 4.5. it's the cheapest way to
# verify your install works end-to-end.

set -e

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "set ANTHROPIC_API_KEY first"
  exit 1
fi

# tests first — no API key needed.
echo "============================================="
echo "  agent-101 speedrun"
echo "============================================="
echo
echo "--- 0. tests (no API call) ---"
python -m pytest tests/ -q

# foundations: one short prompt each.
echo
echo "--- ch00 welcome ---"
python -m chapters.ch00_welcome "what is 17 * 23 in one sentence"

echo
echo "--- ch01 raw_call ---"
python -m chapters.ch01_raw_call "what is 1+1 in one sentence"

echo
echo "--- ch03 stop_reasons ---"
python -m chapters.ch03_stop_reasons

echo
echo "--- ch04 one_tool ---"
python -m chapters.ch04_one_tool "what is 7 * 13?"

echo
echo "--- ch05 the_loop ---"
python -m chapters.ch05_the_loop "list the python files in chapters/, just names, no contents"

echo
echo "--- ch06 parallel_tools ---"
python -m chapters.ch06_parallel_tools

echo
echo "--- ch07 errors ---"
python -m chapters.ch07_errors

echo
echo "--- ch08 system_prompts ---"
python -m chapters.ch08_system_prompts

echo
echo "--- ch10 compaction (this hits the API multiple times) ---"
python -m chapters.ch10_compaction

echo
echo "--- ch11 subagents ---"
python -m chapters.ch11_subagents

echo
echo "--- ch12 skills ---"
python -m chapters.ch12_skills

echo
echo "--- ch13 mcp_wire (real subprocess) ---"
python -m chapters.ch13_mcp_wire

echo
echo "--- ch14 mcp_agent (subprocess + LLM) ---"
python -m chapters.ch14_mcp_agent "what is (17 * 23) + 1234?"

echo
echo "============================================="
echo "  speedrun complete."
echo "  next: try ./agent.py 'your prompt here'"
echo "  or:   python microsite/build_site.py 'a brooklyn ramen shop'"
echo "============================================="
