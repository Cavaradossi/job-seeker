#!/usr/bin/env python3
"""scripts/i18n_audit.py — i18n moat audit (Phase 5).

Static scan of the toolkit for leftover single-script / ASCII-only assumptions
and for "CJK-first / Chinese<->English" framing that contradicts the
script-agnostic moat (every writing system first-class). Advisory by default:
prints a report and exits 0. With ``--strict`` it exits 1 if any ERROR-level
finding is reported, so it can gate CI.

What it checks
--------------
A. Hardcoded CN/EN variant pair in code (should glob ``LaTeX_Resume_*`` instead).
B. ASCII-only tokenizers (``[A-Za-z]`` regexes) that drop non-Latin scripts.
C. "CJK-first" / "Chinese<->English i18n" framing reintroduced into skill docs.
D. Positive confirmations that the any-script rendering infra is wired (INFO).

Run: ``python scripts/i18n_audit.py``  (or ``python -m job_seeker i18n-audit``).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAN_PY_DIRS = ["apply", "convert", "job_seeker"]
SCAN_SHELL_FILES = ["build_resumes.sh", "build_resumes.ps1"]
DOC_DIRS = ["docs/skill"]

# Files that legitimately implement the script-aware tokenizer (no false alarms).
_TOKENIZER_ALLOW = {
    "convert/ats_check.py",
    "job_seeker/tailor.py",
    "job_seeker/cover_letter.py",
}

# A. hardcoded CN/EN literal pair without a glob fallback.
_HARDCODED_PAIR_RE = re.compile(r"LaTeX_Resume_CN")
# B. ASCII-only tokenizer smell (identifier/word regex restricted to A-Za-z).
_ASCII_TOKEN_RE = re.compile(r'\[A-Za-z\][A-Za-z\-{},\*]*|r"[^"]*\[A-Za-z\][^"]*"|re\.compile\([^)]*\[A-Za-z\]')
# C. old framing claims (the moat is "any language", not "Chinese<->English").
_FRAMING_RE = re.compile(r"CJK-first|Chinese.{0,3}English i18n|中文.{0,3}英文 i18n|bilingual i18n", re.IGNORECASE)
# B-exclusion: lines that are clearly doing LaTeX command mangling, not text tokenizing.
_LATEX_CMD_RE = re.compile(r"\\\\(?:section|begin|end|item|textbf|href|centerline|name|contactInfo|datedsubsection|datedline|vspace|pagenumbering)")


@dataclass
class Finding:
    level: str          # ERROR | WARN | INFO
    code: str
    path: str
    line: int = 0
    detail: str = ""

    def as_line(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line else self.path
        return f"[{self.level}] {self.code:10} {loc}  {self.detail}"


@dataclass
class AuditReport:
    findings: list = field(default_factory=list)

    def add(self, *a, **k) -> None:
        self.findings.append(Finding(*a, **k))

    def errors(self) -> int:
        return sum(1 for f in self.findings if f.level == "ERROR")

    def warnings(self) -> int:
        return sum(1 for f in self.findings if f.level == "WARN")

    def format_text(self) -> str:
        lines = ["i18n moat audit"]
        if not self.findings:
            lines.append("  (no findings)")
            return "\n".join(lines)
        for f in sorted(self.findings, key=lambda x: (x.level != "ERROR", x.level != "WARN", x.path)):
            lines.append("  " + f.as_line())
        lines.append(f"  summary: {self.errors()} ERROR, {self.warnings()} WARN")
        return "\n".join(lines)


def _is_test_file(p: Path) -> bool:
    """True for test modules — they legitimately contain example violations."""
    name = p.name
    if name.startswith("test_") or name.endswith("_test.py"):
        return True
    return "tests" in p.parts


def _py_files(root: Path = ROOT) -> list[Path]:
    out = []
    for d in SCAN_PY_DIRS:
        p = root / d
        if p.is_dir():
            for f in p.rglob("*.py"):
                if _is_test_file(f):
                    continue
                out.append(f)
    return out


def _doc_files(root: Path = ROOT) -> list[Path]:
    out = []
    for d in DOC_DIRS:
        p = root / d
        if p.is_dir():
            out.extend(p.rglob("*.md"))
    return out


def _check_hardcoded_pair(report: AuditReport, root: Path = ROOT) -> None:
    """Flag code that hardcodes the CN/EN pair without a glob/discovery helper.

    A true "hardcoded pair" needs BOTH LaTeX_Resume_CN and LaTeX_Resume_EN
    literals in logic (a docstring example mentioning one variant is fine). We
    also tolerate files that glob LaTeX_Resume_* or use _discover_variant_dirs.
    """
    for f in _py_files(root):
        rel = f.relative_to(root).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        has_cn = "LaTeX_Resume_CN" in text
        has_en = "LaTeX_Resume_EN" in text
        if not (has_cn and has_en):
            continue
        # OK if it globs LaTeX_Resume_* or uses the discovery helper.
        if "LaTeX_Resume_*" in text or "_discover_variant_dirs" in text or "glob" in text:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if "LaTeX_Resume_CN" in line or "LaTeX_Resume_EN" in line:
                report.add("ERROR", "HARDCODED_PAIR", rel, i,
                           "hardcoded LaTeX_Resume_CN/EN pair without LaTeX_Resume_* glob")


def _check_ascii_tokenizer(report: AuditReport, root: Path = ROOT) -> None:
    """Flag ASCII-only tokenizers outside the allowlisted script-aware files."""
    for f in _py_files(root):
        rel = f.relative_to(root).as_posix()
        if rel in _TOKENIZER_ALLOW:
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if _ASCII_TOKEN_RE.search(line) and not _LATEX_CMD_RE.search(line):
                report.add("WARN", "ASCII_TOKEN", rel, i,
                           "possible ASCII-only tokenizer (drops non-Latin scripts)")


def _check_framing(report: AuditReport, root: Path = ROOT) -> None:
    """Flag reintroduced CJK-first / Chinese<->English i18n framing in skill docs."""
    for f in _doc_files(root):
        rel = f.relative_to(root).as_posix()
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            m = _FRAMING_RE.search(line)
            if m:
                report.add("ERROR", "OLD_FRAMING", rel, i,
                           f"reintroduces old framing: '{m.group(0)}'")


def _check_rendering_infra(report: AuditReport, root: Path = ROOT) -> None:
    """Positive confirmations that any-script rendering is wired."""
    cls = root / "resume_template" / "resume.cls"
    if cls.is_file() and "fonts_any_script" in cls.read_text(encoding="utf-8", errors="replace"):
        report.add("INFO", "RENDER_OK", "resume_template/resume.cls",
                   detail="loads fonts_any_script.sty (ucharclasses any-script font switch)")
    else:
        report.add("ERROR", "RENDER_MISSING", "resume_template/resume.cls",
                   detail="does not load fonts_any_script.sty")
    sty = root / "resume_template" / "fonts_any_script.sty"
    if sty.is_file():
        txt = sty.read_text(encoding="utf-8", errors="replace")
        report.add("INFO", "UCHARCLASSES", "resume_template/fonts_any_script.sty",
                   detail=f"ucharclasses present: {'ucharclasses' in txt}")
    # shell build scripts must glob, not hardcode the pair
    for name in SCAN_SHELL_FILES:
        p = root / name
        if not p.is_file():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        if "LaTeX_Resume_*" in txt:
            report.add("INFO", "BUILD_GLOB", name, detail="build script globs LaTeX_Resume_*")
        elif "LaTeX_Resume_CN" in txt and "LaTeX_Resume_EN" in txt:
            report.add("WARN", "BUILD_HARDCODED", name,
                       detail="build script references CN/EN without a glob")


def run_audit(root: Path = ROOT) -> AuditReport:
    report = AuditReport()
    _check_hardcoded_pair(report, root)
    _check_ascii_tokenizer(report, root)
    _check_framing(report, root)
    _check_rendering_infra(report, root)
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="i18n moat audit (Phase 5)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any ERROR-level finding is reported")
    args = ap.parse_args(argv)
    report = run_audit()
    print(report.format_text())
    if args.strict and report.errors():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
