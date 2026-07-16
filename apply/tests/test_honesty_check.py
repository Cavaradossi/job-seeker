"""Tests for apply/honesty_check.py (Phase 2.2)."""
from __future__ import annotations

from apply.honesty_check import (
    HonestyReport,
    Finding,
    check_text,
    run_honesty_check,
)


def _ids(rep):
    return {f.rule_id for f in rep.findings}


def test_clean_text_has_no_findings():
    rep = check_text("Improved p99 latency by 38% through query caching.\n"
                     "Led a 4-engineer team maintaining the ETL platform.")
    assert rep.clean is True
    assert rep.findings == []


def test_vague_superlative_flagged():
    rep = check_text("Built a world-class, best-in-class ingestion pipeline.")
    assert "vague-superlative" in _ids(rep)


def test_academic_master_not_flagged():
    # "Master student" / "Master's degree" are legitimate, not puffery
    rep = check_text("Master student in CS; passed Code Master(C++) exam.")
    assert "vague-superlative" not in _ids(rep)


def test_absolute_claim_flagged():
    rep = check_text("The system had zero bugs and 100% uptime, always stable.")
    assert "absolute-claim" in _ids(rep)


def test_scope_inflation_flagged():
    rep = check_text("I independently developed all APIs from scratch.")
    assert "scope-inflation" in _ids(rep)
    # the §6.1 "trading system" boundary example
    rep2 = check_text("Our open-source project is a live trading system.")
    assert "scope-inflation" in _ids(rep2)


def test_uncontextualized_number_flagged():
    rep = check_text("Delivered a 30% improvement across the board.")
    # "improvement" is in the metric verb set -> should NOT flag
    assert "uncontextualized-number" not in _ids(rep)
    rep2 = check_text("Handled 10x the traffic seamlessly.")
    # "traffic" not a metric verb -> flag
    assert "uncontextualized-number" in _ids(rep2)


def test_line_numbers_recorded():
    text = "line one\nline two with world-class claim\nline three"
    rep = check_text(text)
    assert rep.findings
    assert rep.findings[0].line == 2


def test_run_honesty_check_on_file(tmp_path):
    p = tmp_path / "r.tex"
    p.write_text("Used a flawless, revolutionary approach.\n", encoding="utf-8")
    rep = run_honesty_check(str(p))
    assert isinstance(rep, HonestyReport)
    assert not rep.clean


def test_format_text_renders():
    rep = check_text("We are a ninja team, best-in-class.")
    out = rep.format_text()
    assert "Honesty check" in out
    assert "ninja" in out or "best-in-class" in out
