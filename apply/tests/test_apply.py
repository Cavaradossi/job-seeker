"""Tests for the apply package (Phase 3).

Deterministic: no network, no browser, no Playwright required. The
human-in-the-loop gate is exercised via JOB_SEEKER_CONFIRM env + non-tty
stdin. Live browser prefill is covered by the architecture + docs, not here.
"""
from __future__ import annotations

import types
from pathlib import Path

import pytest

from convert.tools import resolve
from apply.adapters import pick_adapter, BossZhipinAdapter, LinkedInAdapter, GenericAdapter
from apply.adapters.base import JDText
from apply.adapters.workday_generic import GenericAdapter as GA
from apply.mapping.jd_to_variant import recommend_variant

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_JD = ROOT / "apply" / "samples" / "sample_jd.html"
HAS_XELATEX = resolve("xelatex") is not None


# ---------------------------------------------------------------- adapter pick
def test_pick_adapter_by_host():
    assert isinstance(pick_adapter("https://www.zhipin.com/job/123"), BossZhipinAdapter)
    assert isinstance(pick_adapter("https://www.linkedin.com/jobs/view/1"), LinkedInAdapter)
    assert isinstance(pick_adapter("https://boards.greenhouse.io/acme/jobs/1"), GenericAdapter)
    assert isinstance(pick_adapter("https://example.com/jobs/123"), GenericAdapter)


def test_tos_flags():
    assert BossZhipinAdapter().tos_blocks_automation is True
    assert LinkedInAdapter().tos_blocks_automation is True
    assert GenericAdapter().tos_blocks_automation is False


# --------------------------------------------------------------- variant rules
def test_recommend_backend():
    jd = JDText(url="x", title="Senior Backend Engineer",
                raw_text="kubernetes devops sre infrastructure platform")
    r = recommend_variant(jd)
    assert r.variant == "resume_backend_ops"
    assert r.matched_keywords


def test_recommend_ai():
    jd = JDText(url="x", title="AI Eval Engineer", raw_text="llm rag benchmark model inference")
    assert recommend_variant(jd).variant == "resume_ai_eval"


def test_recommend_web3():
    jd = JDText(url="x", title="Web3 Engineer", raw_text="solidity ethereum defi smart contract")
    assert recommend_variant(jd).variant == "resume_web3"


def test_recommend_default_en():
    jd = JDText(url="x", title="Software Engineer", raw_text="general software engineering role")
    assert recommend_variant(jd).variant == "resume_job_en"


def test_recommend_default_cn():
    jd = JDText(url="x", title="软件工程师", raw_text="通用软件研发岗位 后端开发")
    assert recommend_variant(jd).variant == "resume-zh_job"


# --------------------------------------------------------------- read_jd (file)
def test_read_jd_local_html():
    from apply.cli import read_jd
    adapter = pick_adapter("")
    args = types.SimpleNamespace(jd_file=str(SAMPLE_JD), url=None)
    jd = read_jd(adapter, args)
    assert jd.source == "local-file"
    assert "backend" in jd.raw_text.lower() or "backend engineer" in jd.raw_text.lower()


# --------------------------------------------------------------- confirm gate
def test_confirm_env_yes(monkeypatch):
    monkeypatch.setenv("JOB_SEEKER_CONFIRM", "yes")
    from apply.confirm import confirm
    assert confirm() is True


def test_confirm_env_no(monkeypatch):
    monkeypatch.setenv("JOB_SEEKER_CONFIRM", "no")
    from apply.confirm import confirm
    assert confirm() is False


def test_confirm_noninteractive_defaults_no(monkeypatch):
    monkeypatch.delenv("JOB_SEEKER_CONFIRM", raising=False)
    from apply.confirm import confirm
    # pytest stdin is not a tty -> safe default NO, never hangs
    assert confirm() is False


# ----------------------------------------- iron rule: submit() calls confirm()
def test_submit_calls_confirm_and_blocks(monkeypatch, capsys):
    """submit() must invoke confirm() before any action (§3.1)."""
    monkeypatch.setenv("JOB_SEEKER_CONFIRM", "no")
    jd = JDText(url="u", title="Role", company="Acme")
    # page=None: even if confirmed, nothing is submitted; with auto-no it must
    # short-circuit at the confirm gate and return False.
    assert GA().submit(jd, page=None) is False
    assert "auto-denied" in capsys.readouterr().out


def test_submit_approved_but_no_browser_returns_false(monkeypatch, capsys):
    """Approved + no browser session => no real submission (honest)."""
    monkeypatch.setenv("JOB_SEEKER_CONFIRM", "yes")
    jd = JDText(url="u", title="Role", company="Acme")
    assert GA().submit(jd, page=None) is False
    out = capsys.readouterr().out
    assert "auto-approved" in out
    assert "no browser session" in out


# ----------------------------------------------------------------- CLI flows
@pytest.mark.skipif(not HAS_XELATEX, reason="xelatex not installed")
def test_cli_dry_run(tmp_path, monkeypatch):
    import apply.audit
    import apply.mapping.variant_renderer as vr
    import apply.cli
    monkeypatch.setattr(apply.audit, "TRACKER", tmp_path / "tracker.csv")
    monkeypatch.setattr(apply.audit, "HISTORY", tmp_path / "history")
    monkeypatch.setattr(vr, "OUT", tmp_path)
    rc = apply.cli.main(["--jd-file", str(SAMPLE_JD),
                         "--variant", "sample-resume-en_US-zh_CN", "--dry-run"])
    assert rc == 0
    assert (tmp_path / "tracker.csv").exists()
    assert "dry_run" in (tmp_path / "tracker.csv").read_text()
    pdf = tmp_path / "sample-resume-en_US-zh_CN_applied.pdf"
    assert pdf.exists() and pdf.stat().st_size > 1000


def test_cli_rehearse_auto_no(tmp_path, monkeypatch):
    import apply.audit
    import apply.mapping.variant_renderer as vr
    import apply.cli
    monkeypatch.setattr(apply.audit, "TRACKER", tmp_path / "tracker.csv")
    monkeypatch.setattr(apply.audit, "HISTORY", tmp_path / "history")
    monkeypatch.setattr(vr, "OUT", tmp_path)
    monkeypatch.setenv("JOB_SEEKER_CONFIRM", "no")
    rc = apply.cli.main(["--jd-file", str(SAMPLE_JD), "--rehearse"])
    assert rc == 0
    content = (tmp_path / "tracker.csv").read_text()
    assert "rehearse_cancelled" in content
