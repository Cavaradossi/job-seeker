"""ATS readability check for resume PDFs (Phase 2.1).

Uses PyMuPDF (fitz, already a dependency — no new installs) to inspect the
PDF *text layer* the way an Applicant Tracking System would:

  1. text-layer present  — the PDF has real, extractable text (not just a
     scanned image of text). ATS parsers only read the text layer.
  2. images-as-text      — flags pages where the glyphs are rasterized into
     images with little/no embedded text (the #1 ATS killer).
  3. tofu / missing glyphs — detects the Unicode replacement char (U+FFFD)
     and non-embedded non-base14 fonts (high risk of boxes on a recruiter's
     machine that lacks your system font; especially fatal for non-Latin text:
     CJK, Cyrillic, Greek, Arabic, Hebrew, Devanagari, …). Script detection is
     writing-system-agnostic — every script is a first-class citizen.
  4. contact info         — email + phone presence (so the parser can route
     your application).
  5. JD keyword coverage  — optional: given the job description text, report
     what fraction of its salient keywords your resume already contains and
     list the missing ones (actionable for tailoring).

The check is **advisory and non-blocking**: it returns a structured
``AtsReport`` and prints a human-readable summary. It never fails a build on
its own; callers decide whether to gate on ``report.errors``.

Example
-------
    from convert.ats_check import run_ats_check
    rep = run_ats_check("outputs/resume_applied.pdf", jd_text=jd)
    print(rep.format_text())
    if rep.errors:
        ...  # optional hard gate
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover - dependency guard
    raise ImportError(
        "PyMuPDF (fitz) is required for the ATS check. "
        "Install with:  pip install 'PyMuPDF>=1.24'"
    ) from exc


# --------------------------------------------------------------------------- #
# Regex / tokenization helpers
# --------------------------------------------------------------------------- #
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# Lenient international phone: optional +, 7-15 digits amid separators.
PHONE_RE = re.compile(r"(?:\+?\d[^\d\n]{0,2})?(?:\(?\d{2,4}\)?[\s.\-]?){2,5}\d")
# Script-coverage map: Unicode BMP/SMP ranges per writing system, used to detect
# which scripts appear in a resume's text layer so tofu / non-embedded-font
# warnings can be script-specific (not just "CJK"). Ranges are conservative
# (common blocks only) — enough to flag risk, not a full Unicode script table.
# Every writing system is a first-class citizen here.
SCRIPT_RANGES = {
    "latin":     r"[\u0041-\u005a\u0061-\u007a\u00c0-\u024f\u1e00-\u1eff]",
    "cjk":       r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef\U00020000-\U0002a6df]",
    "cyrillic":  r"[\u0400-\u04ff\u0500-\u052f\u2de0-\u2dff\ua640-\ua69f]",
    "greek":     r"[\u0370-\u03ff\u1f00-\u1fff]",
    "arabic":    r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]",
    "hebrew":    r"[\u0590-\u05ff\ufb1d-\ufb4f]",
    "devanagari": r"[\u0900-\u097f\ua8e0-\ua8ff]",
}
# A glyph rendered as a box is often the replacement char or a control box.
_TOFU_CHARS = {"\ufffd", "\u25af", "\u25a1", "\u274f", "\u2751"}

# PDF base-14 fonts are always available to viewers, so "not embedded" is safe.
_BASE14 = {
    "helvetica", "helvetica-bold", "helvetica-oblique", "helvetica-boldoblique",
    "times-roman", "times-bold", "times-italic", "times-bolditalic",
    "courier", "courier-bold", "courier-oblique", "courier-boldoblique",
    "symbol", "zapfdingbats",
}

_STOPWORDS = {
    "the", "and", "for", "with", "you", "our", "are", "but", "not", "have",
    "this", "that", "will", "from", "your", "all", "can", "who", "out", "use",
    "using", "into", "than", "then", "they", "their", "them", "such", "more",
    "most", "some", "what", "when", "where", "which", "while", "about", "over",
    "also", "any", "per", "via", "etc", "inc", "ltd", "llc", "co", "corp",
    "job", "work", "role", "team", "ability", "experience", "years", "year",
    "new", "one", "two", "three", "must", "able", "other", "these", "those",
    "were", "been", "being", "each", "does", "doing", "how", "why", "should",
}

# Script-aware tokenizer: any run of Unicode letters/marks, not just ASCII. This
# makes keyword coverage / skill-gap analysis work for Cyrillic, Arabic, Hebrew,
# Devanagari, Greek, CJK, etc. — the old ASCII-only regex returned 0 tokens for
# non-Latin JDs, faking "100% coverage". Dependency-free (unicodedata, no `regex`).
def script_aware_tokens(text: str) -> dict:
    """Tokenize `text` into a {token: count} map across any writing system.

    A token is a maximal run of >= 3 Unicode letters or combining marks. English
    stopwords are filtered; non-Latin scripts have no stopword filtering (count,
    not lexicon, drives coverage). Works for Latin, Cyrillic, CJK, Arabic,
    Hebrew, Devanagari, Greek, and more.
    """
    out: dict = {}
    if not text:
        return out
    text = unicodedata.normalize("NFC", (text or "").lower())
    run: list = []

    def _flush() -> None:
        if run and len(run) >= 3:
            tok = "".join(run)
            if tok not in _STOPWORDS:
                out[tok] = out.get(tok, 0) + 1
        run.clear()

    for ch in text:
        cat = unicodedata.category(ch)
        if cat[0] == "L" or cat in ("Mn", "Mc"):   # Letter or combining mark
            run.append(ch)
        else:
            _flush()
    _flush()
    return out



# --------------------------------------------------------------------------- #
# Report model
# --------------------------------------------------------------------------- #
@dataclass
class AtsReport:
    """Structured result of an ATS readability check."""

    pdf: str = ""
    pages: int = 0
    glyph_cells: int = 0         # glyph cells detected across all pages
    text_chars: int = 0          # chars actually mapped in the text layer
    replacement_chars: int = 0   # U+FFFD etc. in the text layer
    scripts_present: set = field(default_factory=set)  # writing systems found
    nonembedded_fonts: bool = False
    images_as_text: bool = False
    has_email: bool = False
    has_phone: bool = False
    jd_coverage: Optional[float] = None      # 0..1, None if no JD given
    missing_keywords: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    score: int = 100             # 0..100 advisory score

    # -- presentation ----------------------------------------------------- #
    def format_text(self) -> str:
        lines = []
        lines.append("ATS readability check")
        lines.append(f"  file : {self.pdf}")
        lines.append(f"  pages: {self.pages}  |  text chars: {self.text_chars}  "
                     f"|  score: {self.score}/100")
        if self.replacement_chars:
            lines.append(f"  [ERROR ] {self.replacement_chars} Unicode replacement "
                         f"char(s) (U+FFFD) in the text layer.")
        if self.nonembedded_fonts:
            at_risk = sorted(s for s in self.scripts_present if s != "latin")
            scripts = ", ".join(at_risk) if at_risk else "non-Latin"
            lines.append("  [WARN  ] Uses non-embedded fonts (not base-14) — high "
                         f"risk of tofu/boxes on machines lacking your system font "
                         f"(scripts at risk: {scripts}).")
        non_latin = sorted(s for s in self.scripts_present if s != "latin")
        if non_latin:
            lines.append(f"  [INFO  ] Writing systems detected: {', '.join(non_latin)}")
        if self.images_as_text:
            lines.append("  [WARN  ] Text appears rasterized (images-as-text) on "
                         "some pages — ATS cannot read it.")
        if not self.has_email:
            lines.append("  [WARN  ] No email address found in the text layer.")
        if not self.has_phone:
            lines.append("  [WARN  ] No phone number found in the text layer.")
        if self.jd_coverage is not None:
            pct = int(round(self.jd_coverage * 100))
            lines.append(f"  [INFO  ] JD keyword coverage: {pct}%")
            if self.missing_keywords:
                shown = ", ".join(self.missing_keywords[:15])
                more = "" if len(self.missing_keywords) <= 15 else \
                    f" …(+{len(self.missing_keywords) - 15} more)"
                lines.append(f"  [INFO  ] Missing keywords: {shown}{more}")
        if self.errors:
            lines.append("  errors : " + "; ".join(self.errors))
        if self.warnings:
            lines.append("  warnings: " + "; ".join(self.warnings))
        if not self.errors and not self.warnings \
                and self.jd_coverage is None:
            lines.append("  [OK    ] Text layer looks ATS-friendly.")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Pure helpers (unit-testable)
# --------------------------------------------------------------------------- #
def _detect_scripts(text: str) -> set:
    """Return the set of writing-system tags present in `text`."""
    if not text:
        return set()
    found = set()
    for tag, rx in SCRIPT_RANGES.items():
        if re.search(rx, text):
            found.add(tag)
    return found


def _has_script(text: str, tag: str) -> bool:
    """True if `text` contains any codepoint from the given writing system."""
    rx = SCRIPT_RANGES.get(tag)
    return bool(rx and re.search(rx, text))


def _cjk_runs(text: str) -> bool:
    """Deprecated alias for ``_has_script(text, "cjk")`` — kept for tests."""
    return _has_script(text, "cjk")


def _count_replacement(text: str) -> int:
    return sum(text.count(c) for c in _TOFU_CHARS)


def _is_base14(basefont: Optional[str]) -> bool:
    if not basefont:
        return False
    name = basefont.lower().split("+")[-1]
    return name in _BASE14


def _font_has_tofu_risk(fonts: list) -> bool:
    """True if any font is non-embedded and not a safe base-14 font.

    ``fonts`` entries follow PyMuPDF ``page.get_fonts(full=True)``:
    (xref, ext, type, basefont, name, encoding, reference). ``ext`` is the
    embedded font-file extension (None == not embedded).
    """
    for f in fonts:
        ext, basefont = f[1], f[3]
        if ext is None and not _is_base14(basefont):
            return True
    return False


def _page_glyph_cells(raw: dict) -> int:
    n = 0
    for block in raw.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                n += len(span.get("chars", []))
    return n


def _keyword_coverage(resume_text: str, jd_text: str) -> tuple[float, list]:
    """Return (coverage 0..1, missing_keywords_sorted_by_frequency).

    Uses `script_aware_tokens` so non-Latin JDs/resumes are compared correctly.
    """
    rt = script_aware_tokens(resume_text)
    jt = script_aware_tokens(jd_text)
    if not jt:
        return 1.0, []
    present = {k for k in jt if k in rt}
    total = sum(jt.values())
    covered = sum(jt[k] for k in present)
    coverage = covered / total if total else 1.0
    missing = sorted(
        (k for k in jt if k not in rt),
        key=lambda k: jt[k], reverse=True,
    )
    return coverage, missing


# --------------------------------------------------------------------------- #
# Core checks
# --------------------------------------------------------------------------- #
def _check_text_layer(doc: "fitz.Document", report: AtsReport) -> None:
    """Detect pages where text is rasterized (images-as-text)."""
    for pno in range(doc.page_count):
        page = doc[pno]
        imgs = page.get_images(full=True)
        raw = page.get_text("rawdict")
        glyphs = _page_glyph_cells(raw)
        text_len = len(page.get_text("text").strip())
        report.glyph_cells += glyphs
        report.text_chars += text_len
        if imgs and text_len < max(40, glyphs * 0.2):
            report.images_as_text = True
            report.warnings.append(
                f"page {pno + 1}: image(s) present but little extractable text"
            )


def _check_tofu(doc: "fitz.Document", report: AtsReport) -> None:
    """Detect replacement chars and non-embedded (tofu-risk) fonts."""
    for pno in range(doc.page_count):
        page = doc[pno]
        txt = page.get_text("text")
        report.replacement_chars += _count_replacement(txt)
        report.scripts_present |= _detect_scripts(txt)
        if _font_has_tofu_risk(page.get_fonts(full=True)):
            report.nonembedded_fonts = True


def _check_contact(text: str, report: AtsReport) -> None:
    report.has_email = bool(EMAIL_RE.search(text))
    for m in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if len(digits) >= 7:
            report.has_phone = True
            break


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def run_ats_check(pdf_path: str,
                  jd_text: Optional[str] = None,
                  name: Optional[str] = None) -> AtsReport:
    """Run all ATS readability checks on ``pdf_path``.

    ``jd_text`` enables keyword-coverage analysis. ``name`` is an optional
    candidate name (reserved for future contact-info checks).
    Returns an :class:`AtsReport`.
    """
    report = AtsReport(pdf=pdf_path)
    doc = fitz.open(pdf_path)
    try:
        report.pages = doc.page_count
        text = "".join(page.get_text("text") for page in doc)

        _check_text_layer(doc, report)
        _check_tofu(doc, report)
        _check_contact(text, report)

        if jd_text:
            cov, missing = _keyword_coverage(text, jd_text)
            report.jd_coverage = cov
            report.missing_keywords = missing

        _score(report)
    finally:
        doc.close()
    return report


def _score(report: AtsReport) -> None:
    """Compute the advisory 0..100 score and finalize errors/warnings."""
    score = 100
    text_ratio = (report.text_chars / report.glyph_cells) \
        if report.glyph_cells else 1.0

    # Text layer quality
    if report.glyph_cells == 0 or report.text_chars == 0:
        report.errors.append("no extractable text layer (likely a scanned image)")
        score -= 45
    elif text_ratio < 0.5:
        report.warnings.append(
            f"only {int(text_ratio * 100)}% of glyphs carry text "
            "(possible images-as-text)"
        )
        score -= 20

    if report.images_as_text:
        score -= 10

    # Tofu / missing glyphs — the hardest ATS failure
    if report.replacement_chars > 0:
        report.errors.append(
            f"{report.replacement_chars} replacement char(s) (U+FFFD)"
        )
        score -= 15
    if report.nonembedded_fonts:
        at_risk = sorted(s for s in report.scripts_present if s != "latin")
        detail = (f" (scripts at risk: {', '.join(at_risk)})"
                  if at_risk else " (non-Latin tofu risk)")
        report.warnings.append("non-embedded fonts (tofu risk)" + detail)
        score -= 12

    # Contact info
    if not report.has_email:
        report.warnings.append("email not found in text layer")
        score -= 10
    if not report.has_phone:
        report.warnings.append("phone not found in text layer")
        score -= 8

    # JD keyword coverage
    if report.jd_coverage is not None:
        if report.jd_coverage < 0.5:
            score -= int(round((0.5 - report.jd_coverage) * 20))

    report.score = max(0, min(100, score))
