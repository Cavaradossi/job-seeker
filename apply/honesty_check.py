"""Heuristic honesty check for resume bullets (Phase 2.2).

A lightweight, *advisory* linter that flags resume claims which tend to trip
the project's honesty boundaries (docs/skill/job-seeker/checklist.md §E and
references/master_prompt_extract.md §6.1):

  1. vague superlatives / unverifiable self-ratings
       ("world-class", "best-in-class", "expert", "guru", "ninja" …)
  2. uncontextualized numbers
       a bare "30%" / "10x" with no metric verb nearby
       (improved / reduced / grew / saved / boosted …) → needs a baseline
  3. absolute claims
       "never", "always", "zero bugs", "100% uptime", "flawless" …
  4. scope-inflation phrasings
       "from scratch", "single-handedly", "independently developed all",
       "autonomous agent", "trading system", "live trading" — these map
       directly to the §6.1 honesty boundaries (POC vs production,
       research-workflow framework vs trading system).

This is a HEURISTIC, not a judgment of truth. It flags *wording* that
frequently correlates with inflated claims so a human (or the SKILL reviewer
pass) can double-check. It never auto-edits. See checklist.md §E for the
human self-audit questions.

Example
-------
    from apply.honesty_check import run_honesty_check
    rep = run_honesty_check("LaTeX_Resume_EN/sample-resume-en_US-zh_CN.tex")
    print(rep.format_text())
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


# Metric verbs that *contextualize* a number (give it a baseline/comparison).
_METRIC_VERBS = {
    "improved", "improve", "improvement", "increased", "increase",
    "reduced", "reduce", "reduction", "decreased", "decrease",
    "grew", "grow", "grown", "saved", "save", "saving", "boosted", "boost",
    "cut", "optimized", "optimise", "optimize", "accelerated", "accelerate",
    "shortened", "raised", "lowered", "delivered", "achieved", "drove",
    "drive", "generated", "yielded", "yield", "shrunk", "shrank", "halved",
}

# (rule_id, human label, regex, advice)
_RULES: List[Tuple[str, str, "re.Pattern", str]] = [
    ("vague-superlative", "vague superlative / unverifiable self-rating",
     re.compile(
         r"\b(world[- ]?class|best[- ]?in[- ]?class|unparalleled|unmatched|"
         r"revolutionary|expert|guru|ninja|rockstar|perfect|"
         r"flawless|state[- ]?of[- ]?the[- ]?art|game[- ]?changing)\b",
         re.IGNORECASE),
     "Replace puffery with a measurable fact; a human reviewer cannot verify "
     "'expert'/'world-class'."),

    ("absolute-claim", "absolute claim",
     re.compile(
         r"\b(never|always|eliminated all|zero (bugs|downtime|errors)|"
         r"100% (uptime|reliability|accuracy)|flawlessly|without any (bug|error))\b",
         re.IGNORECASE),
     "Absolute claims are easy to disprove; soften to what actually happened."),

    ("scope-inflation", "scope-inflation phrasing (honesty boundary §6.1)",
     re.compile(
         r"\b(from scratch|greenfield|single[- ]?handedly|"
         r"independently developed all|autonomous agent|"
         r"trading system|live trading|market[- ]?beating)\b",
         re.IGNORECASE),
     "Verify against §6.1: POC vs production, maintenance vs greenfield, "
     "research-workflow framework vs trading system."),
]

# Numbers that need a metric verb nearby to be honest.
_NUMBER_RE = re.compile(r"\b\d{1,3}\s?%|\b\d{2,}\s?x\b|\b\d{2,}\+?\s?(users|servers|nodes|teams|clients)\b", re.IGNORECASE)


@dataclass
class Finding:
    rule_id: str
    label: str
    line: int
    snippet: str
    advice: str


@dataclass
class HonestyReport:
    source: str = ""
    findings: List[Finding] = field(default_factory=list)
    warnings: list = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not self.findings

    def format_text(self) -> str:
        lines = []
        lines.append("Honesty check (heuristic — advisory, not a verdict)")
        lines.append(f"  source: {self.source}")
        if not self.findings:
            lines.append("  [OK    ] No vague superlatives, absolute claims, or "
                         "scope-inflation phrasing detected.")
            return "\n".join(lines)
        lines.append(f"  {len(self.findings)} item(s) to double-check:")
        for f in self.findings:
            snip = f.snippet.strip().replace("\n", " ")
            if len(snip) > 80:
                snip = snip[:77] + "…"
            lines.append(f"  L{f.line:>3} [{f.rule_id}] {snip}")
            lines.append(f"          → {f.advice}")
        return "\n".join(lines)


def _check_line(rule_id: str, label: str, rx: "re.Pattern",
                advice: str, line_no: int, line: str,
                out: List[Finding]) -> None:
    for m in rx.finditer(line):
        out.append(Finding(rule_id, label, line_no, m.group(0), advice))


def _check_numbers(line_no: int, line: str, out: List[Finding]) -> None:
    low = line.lower()
    has_metric = any(v in low for v in _METRIC_VERBS)
    for m in _NUMBER_RE.finditer(line):
        if not has_metric:
            out.append(Finding(
                "uncontextualized-number",
                "number without a metric verb (no baseline/comparison)",
                line_no, m.group(0),
                "Attach a metric verb (improved/reduced/grew/saved) and a "
                "baseline so the figure is verifiable."))
            break  # one flag per line is enough


def check_text(text: str) -> HonestyReport:
    """Run all heuristic rules over ``text`` (line by line)."""
    rep = HonestyReport()
    for i, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        for rule_id, label, rx, advice in _RULES:
            _check_line(rule_id, label, rx, advice, i, line, rep.findings)
        _check_numbers(i, line, rep.findings)
    return rep


def run_honesty_check(tex_path: str) -> HonestyReport:
    """Read ``tex_path`` and run the honesty check on its contents."""
    rep = HonestyReport(source=tex_path)
    p = Path(tex_path).expanduser()
    text = p.read_text(encoding="utf-8", errors="replace")
    sub = check_text(text)
    rep.findings = sub.findings
    return rep
