"""Tests for skills loading (chapter 12)."""
from pathlib import Path

import importlib.util
import sys


spec = importlib.util.spec_from_file_location(
    "ch12", Path(__file__).resolve().parent.parent / "chapters" / "ch12_skills.py")
ch12 = importlib.util.module_from_spec(spec)
sys.modules["ch12"] = ch12
spec.loader.exec_module(ch12)


def test_parse_skill_md(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("---\nname: testskill\ndescription: test\n---\nbody here\n")
    meta = ch12.parse_skill_md(p)
    assert meta["name"] == "testskill"
    assert meta["description"] == "test"
    assert "body here" in meta["body"]


def test_load_catalog_finds_real_skills():
    catalog = ch12.load_catalog()
    # the repo ships at least the haiku-master and landing-page skills
    assert "haiku-master" in catalog
    assert "landing-page" in catalog
    assert "haiku" in catalog["haiku-master"]["description"].lower()


def test_build_skills_prompt_lists_skills():
    catalog = ch12.load_catalog()
    prompt = ch12.build_skills_prompt(catalog)
    assert "haiku-master" in prompt
    assert "landing-page" in prompt
    # the catalog format must include name and description but NOT the body
    body = catalog["haiku-master"]["body"]
    assert body[:50] not in prompt
