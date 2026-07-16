import pytest

from convert.ats_check import script_aware_tokens, _keyword_coverage


def test_script_aware_tokens_non_latin():
    # The old ASCII-only regex returned 0 tokens for these → fake "100% coverage".
    ru = script_aware_tokens("Ведущий инженер, распределённые системы")
    assert ru, "Cyrillic JD must yield tokens, not 0"
    ar = script_aware_tokens("مهندس برمجيات أول، تطوير واجهات الويب")
    assert ar, "Arabic JD must yield tokens, not 0"
    he = script_aware_tokens("מהנדס תוכנה בכיר, פיתוח מערכות")
    assert he, "Hebrew JD must yield tokens, not 0"
    # Latin still works
    en = script_aware_tokens("Backend engineer with Kubernetes")
    assert "kubernetes" in en


def test_keyword_coverage_non_latin_is_meaningful():
    # A Russian JD vs an empty resume must report a real (low) coverage, not 1.0.
    jd = "Ведущий инженер, Kubernetes и распределённые системы"
    cov, missing = _keyword_coverage("", jd)
    assert cov == 0.0
    assert missing, "non-Latin JD should produce a gap list, not be silently 'covered'"

    # Resume that contains the same Cyrillic keyword should raise coverage.
    resume = "Я ведущий инженер, проектирую распределённые системы"
    cov2, missing2 = _keyword_coverage(resume, jd)
    assert cov2 > 0.0
    assert cov2 < 1.0


def test_runs_split_on_non_letter():
    # Non-letters break runs; runs shorter than 3 letters are dropped.
    toks = script_aware_tokens("Python, Kubernetes (AI skills)")
    assert "python" in toks
    assert "kubernetes" in toks
    assert "skills" in toks
    assert "ai" not in toks   # 2-letter run is dropped (< 3)
