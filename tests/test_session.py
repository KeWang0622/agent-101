"""Tests for the session JSONL round-trip (chapter 9)."""
import json
from pathlib import Path

# import the Session class straight from the chapter file.
import importlib.util
import sys

spec = importlib.util.spec_from_file_location(
    "ch09", Path(__file__).resolve().parent.parent / "chapters" / "ch09_sessions.py")
ch09 = importlib.util.module_from_spec(spec)
sys.modules["ch09"] = ch09


def _load_with_temp_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("os.environ", {**__import__('os').environ, "ANTHROPIC_API_KEY": "x"})
    spec.loader.exec_module(ch09)
    monkeypatch.setattr(ch09, "SESSION_DIR", tmp_path)
    return ch09


def test_session_writes_and_replays(tmp_path, monkeypatch):
    ch = _load_with_temp_dir(tmp_path, monkeypatch)

    s = ch.Session()
    s.append_user("hi")
    s.append_assistant([{"type": "text", "text": "hello"}])
    s.append_tool_results([{"type": "tool_result",
                            "tool_use_id": "x", "content": "42"}])

    # second instance with same id should replay everything
    s2 = ch.Session(s.id)
    assert len(s2.messages) == 3
    assert s2.messages[0] == {"role": "user", "content": "hi"}
    assert s2.messages[1]["role"] == "assistant"
    assert s2.messages[2]["role"] == "user"           # tool_results live in user role


def test_jsonl_format(tmp_path, monkeypatch):
    ch = _load_with_temp_dir(tmp_path, monkeypatch)
    s = ch.Session()
    s.append_user("hi")
    lines = s.path.read_text().splitlines()
    # every line must be valid JSON
    for line in lines:
        json.loads(line)
    # first line must be the meta entry
    assert json.loads(lines[0])["type"] == "meta"
