"""Skill-gap analysis (``--upskill``).

Given a job description and (optionally) the candidate's resume, report the JD
keywords the resume does **not** contain — framed as skills to develop. This is
the "what am I missing for this role?" view that complements the ATS keyword
*coverage* check (which measures how much of the JD you already match).

It reuses the same keyword tokenizer as ``convert.ats_check._keyword_coverage``
so the two views stay consistent. Pure-Python, no new dependencies.

Advisory only — never edits the resume.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from convert.ats_check import _keyword_coverage, _STOPWORDS, script_aware_tokens


@dataclass
class UpskillReport:
    jd_source: str = ""
    resume_source: str = ""
    coverage: float = 0.0          # 0..1, share of JD keywords already present
    present: list = field(default_factory=list)
    gap: list = field(default_factory=list)   # JD keywords absent from resume

    def format_text(self) -> str:
        lines = []
        lines.append("Skill-gap analysis (--upskill)")
        lines.append(f"  JD     : {self.jd_source}")
        lines.append(f"  resume : {self.resume_source or '(none provided)'}")
        lines.append(f"  coverage: {int(round(self.coverage * 100))}% of JD keywords "
                     f"already present")
        if self.gap:
            shown = ", ".join(self.gap[:20])
            more = "" if len(self.gap) <= 20 else f" …(+{len(self.gap) - 20} more)"
            lines.append(f"  [GAP] skills to develop: {shown}{more}")
        else:
            lines.append("  [OK ] resume already covers the JD's salient keywords.")
        return "\n".join(lines)


def _read_text(path: str) -> str:
    from pathlib import Path
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _jd_from_url(url: str) -> str:
    """Best-effort JD text from a URL via the matched adapter (no cli import)."""
    from .adapters import pick_adapter
    adapter = pick_adapter(url)
    jd = adapter.read_jd(url)
    return jd.raw_text or ""


def analyze(jd_text: str, resume_text: Optional[str] = None,
            jd_source: str = "", resume_source: str = "") -> UpskillReport:
    """Compute coverage + gap between ``jd_text`` and ``resume_text``.

    If ``resume_text`` is None/empty, coverage is reported as 0 and the full JD
    keyword set is treated as the gap (i.e. "here is what this role wants").
    """
    if not resume_text:
        cov, missing = _keyword_coverage("", jd_text)
        # _keyword_coverage returns (1.0, []) when resume is empty; recompute gap
        # with the script-aware tokenizer so non-Latin JDs get a real gap list.
        jt = script_aware_tokens(jd_text)
        missing = sorted(jt, key=lambda k: jt[k], reverse=True)
        return UpskillReport(
            jd_source=jd_source, resume_source=resume_source,
            coverage=0.0, present=[], gap=missing,
        )
    cov, missing = _keyword_coverage(resume_text, jd_text)
    present = sorted({t for t in script_aware_tokens(jd_text)
                      if t in script_aware_tokens(resume_text)})
    return UpskillReport(
        jd_source=jd_source, resume_source=resume_source,
        coverage=cov, present=present, gap=missing,
    )


def run_upskill(jd: str, resume: Optional[str] = None) -> UpskillReport:
    """CLI entry: resolve ``jd`` (file URL or path) and ``resume`` (path)."""
    if jd.startswith("http://") or jd.startswith("https://"):
        jd_text = _jd_from_url(jd)
        jd_src = jd
    else:
        from pathlib import Path as _Path
        p = _Path(jd)
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix.lower() in (".html", ".htm"):
            from bs4 import BeautifulSoup
            text = BeautifulSoup(text, "html.parser").get_text(separator="\n")
        jd_text = text
        jd_src = jd
    resume_text = _read_text(resume) if resume else None
    return analyze(jd_text, resume_text, jd_source=jd_src,
                   resume_source=resume or "")


__all__ = ["UpskillReport", "analyze", "run_upskill"]
