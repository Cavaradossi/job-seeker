"""Tests for convert/ats_check.py (Phase 2.1)."""
from __future__ import annotations

import fitz
import pytest

from convert.ats_check import (
    AtsReport,
    run_ats_check,
    _check_contact,
    _keyword_coverage,
    _cjk_runs,
    _count_replacement,
    _is_base14,
    _font_has_tofu_risk,
    _detect_scripts,
    _has_script,
    _score,
)


def _make_pdf(path, text, *, image=False):
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((50, 50), text, fontsize=11)
    if image:
        # a 60x60 white pixmap with no accompanying text exercises
        # the images-as-text path (glyphs=0, text=0).
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 60, 60), False)
        page.insert_image(fitz.IRect(200, 200, 260, 260), pixmap=pix)
    doc.save(path)
    doc.close()


def test_text_layer_present(tmp_path):
    pdf = tmp_path / "ok.pdf"
    _make_pdf(pdf, "Alice Engineer\nalice@example.com\n+1 (415) 555-2671")
    rep = run_ats_check(str(pdf))
    assert rep.pages == 1
    assert rep.text_chars > 0
    assert rep.has_email is True
    assert rep.has_phone is True
    assert rep.replacement_chars == 0
    assert rep.nonembedded_fonts is False  # Helvetica is base-14 => safe
    assert rep.score >= 90


def test_missing_contact_warns(tmp_path):
    pdf = tmp_path / "nope.pdf"
    _make_pdf(pdf, "Just a name, no email or phone here.")
    rep = run_ats_check(str(pdf))
    assert rep.has_email is False
    assert rep.has_phone is False
    assert any("email" in w for w in rep.warnings)
    assert any("phone" in w for w in rep.warnings)


def test_images_as_text_detected(tmp_path):
    pdf = tmp_path / "img.pdf"
    _make_pdf(pdf, "", image=True)
    rep = run_ats_check(str(pdf))
    assert rep.images_as_text is True
    assert rep.errors  # no extractable text layer


def test_count_replacement_unit():
    assert _count_replacement("a\ufffdb") == 1
    assert _count_replacement("clean text") == 0


def test_base14_and_tofu_font_helpers():
    # base-14 whitelisted even when not embedded (ext=None)
    assert _is_base14("Helvetica") is True
    assert _is_base14("ABC+Helvetica-Bold") is True
    assert _is_base14("MyCustomFont") is False
    # non-embedded custom font => tofu risk; base-14 non-embedded => safe
    assert _font_has_tofu_risk([(1, None, "Type1", "MyFont", "", "", None)]) is True
    assert _font_has_tofu_risk([(1, None, "Type1", "Helvetica", "", "", None)]) is False
    assert _font_has_tofu_risk([(1, "ttf", "TrueType", "MyFont", "", "", None)]) is False


def test_keyword_coverage(tmp_path):
    resume = "Python developer with Django and REST APIs"
    jd = ("We need a Python and Kubernetes engineer experienced in Go "
          "and cloud infrastructure.")
    cov, missing = _keyword_coverage(resume, jd)
    assert 0.0 <= cov < 1.0
    assert "kubernetes" in missing
    assert "python" not in missing  # present in resume


def test_jd_coverage_in_report(tmp_path):
    pdf = tmp_path / "cov.pdf"
    _make_pdf(pdf, "Python developer with Django and REST APIs")
    jd = "We need a Python and Kubernetes engineer experienced in Go."
    rep = run_ats_check(str(pdf), jd_text=jd)
    assert rep.jd_coverage is not None
    assert rep.jd_coverage < 1.0
    assert "kubernetes" in rep.missing_keywords


def test_cjk_runs_helper():
    assert _cjk_runs("hello 世界") is True
    assert _cjk_runs("plain ascii only") is False


def test_detect_scripts_covers_all_writing_systems():
    # Every writing system is a first-class citizen — not just CJK.
    assert _detect_scripts("Ведущий инженер") == {"cyrillic"}
    assert _detect_scripts("مطور برمجيات") == {"arabic"}
    assert _detect_scripts("מפתח תוכנה") == {"hebrew"}
    assert _detect_scripts("सॉफ्टवेयर डेवलपर") == {"devanagari"}
    assert _detect_scripts("προγραμματιστής") == {"greek"}
    assert _detect_scripts("软件工程师") == {"cjk"}
    # Mixed Latin + non-Latin returns both tags.
    assert _detect_scripts("Python разработчик") == {"latin", "cyrillic"}
    # Plain ASCII is detected as latin, not "unknown"/empty.
    assert _detect_scripts("plain ascii only") == {"latin"}


def test_has_script_helper():
    assert _has_script("软件工程师", "cjk") is True
    assert _has_script("software engineer", "cjk") is False
    assert _has_script("مطور", "arabic") is True


def test_nonembedded_warning_names_scripts():
    rep = AtsReport(pdf="x", nonembedded_fonts=True,
                    scripts_present={"cyrillic", "greek"})
    _score(rep)
    assert any("cyrillic" in w and "greek" in w for w in rep.warnings)


def test_format_text_script_specific():
    rep = AtsReport(pdf="x", nonembedded_fonts=True,
                    scripts_present={"arabic", "hebrew"})
    out = rep.format_text()
    assert "arabic" in out and "hebrew" in out


def test_report_format_text(tmp_path):
    pdf = tmp_path / "f.pdf"
    _make_pdf(pdf, "Bob\ndrop@cv.io\n+86 138 0013 8000")
    rep = run_ats_check(str(pdf))
    out = rep.format_text()
    assert "ATS readability check" in out
    assert "score:" in out


def test_ats_check_returns_report_type(tmp_path):
    pdf = tmp_path / "r.pdf"
    _make_pdf(pdf, "Minimal resume text for smoke test.")
    rep = run_ats_check(str(pdf))
    assert isinstance(rep, AtsReport)
