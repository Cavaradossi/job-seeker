"""Tests for job_seeker.cover_letter (Phase 4)."""
from __future__ import annotations

from job_seeker.cover_letter import run_cover_letter

BANK = """\
## Role: SRE @ Acme (2020-2022)

### Bullet material

- Built Kubernetes platform serving 10k pods
- Reduced latency by 40% through caching
"""


def test_cover_letter_latin_uses_english_template():
    jd = "We need an SRE with Kubernetes and platform experience."
    out = run_cover_letter(jd, BANK, name="Jane Doe", jd_source="acme")
    assert "DRAFT" in out
    assert "Dear Hiring Manager," in out
    assert "Sincerely," in out
    assert "Jane Doe" in out
    # a matched bullet is cited
    assert "Kubernetes" in out


def test_cover_letter_cjk_uses_chinese_template():
    jd = "我们需要一位熟悉 Kubernetes 平台的工程师"
    out = run_cover_letter(jd, BANK, name="张三", jd_source="cn")
    assert "尊敬的" in out
    assert "此致" in out
    assert "张三" in out
    assert "DRAFT" in out


def test_cover_letter_other_script_falls_back_with_note():
    # Cyrillic JD -> no native template -> LATIN fallback + localize note
    jd = "Ищем инженера платформы Kubernetes"  # Russian
    out = run_cover_letter(jd, BANK, name="Ivan", jd_source="ru")
    assert "Dear Hiring Manager," in out
    assert "localize" in out.lower()
    assert "cyrillic" in out.lower()


def test_cover_letter_marks_fallback_when_no_matches():
    jd = "zzz qqq xxx yyy"  # no token overlap with the bank
    out = run_cover_letter(jd, BANK, name="A", jd_source="x")
    # still produces a draft, and warns about no matches
    assert "DRAFT" in out
    assert "no" in out.lower() and "matched" in out.lower()
