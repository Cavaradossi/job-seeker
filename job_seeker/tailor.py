"""job_seeker/tailor.py — JD + experience bank -> tailored resume variant (Phase 4).

Offline, rule-based, no external API. Implements the SKILL §4.5 "drafter" pass:
read a JD and the candidate's experience bank, score each bullet by keyword
overlap with the JD, select the strongest matches, and (optionally) write a
tailored .tex variant by substituting a marked experience block of the base
template. It never invents bullets — only reuses material already in the bank.

Marker convention in a base .tex (script-tagged, optional):

    % >>> TAILOR BLOCK LATIN START
    ... experience itemize content ...
    % >>> TAILOR BLOCK LATIN END

Matching <SCRIPT> tags: LATIN, CJK, CYRILLIC, ARABIC, HEBREW, DEVANAGARI, GREEK.
If no block matches the JD's script, the LATIN block is used with a warning; if
no markers exist at all, a .tex snippet + Markdown report are emitted instead
(no .tex rewrite). This keeps .tex editing reversible and offline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from convert.ats_check import script_aware_tokens, _keyword_coverage
from apply.mapping.jd_to_variant import detect_script, Script

# Script enum -> marker tag used inside a .tex, and the reverse map.
_SCRIPT_TAG = {
    Script.LATIN: "LATIN",
    Script.CJK: "CJK",
    Script.CYRILLIC: "CYRILLIC",
    Script.ARABIC: "ARABIC",
    Script.HEBREW: "HEBREW",
    Script.DEVANAGARI: "DEVANAGARI",
    Script.GREEK: "GREEK",
}
_TAG_TO_SCRIPT = {v: k for k, v in _SCRIPT_TAG.items()}

_MARKER_RE = re.compile(
    r"% >>> TAILOR BLOCK (?P<tag>[A-Z]+) START\n(.*?)\n% >>> TAILOR BLOCK (?P=tag) END",
    re.DOTALL,
)


@dataclass
class Bullet:
    text: str
    role: str = ""
    component: str = ""


@dataclass
class TailorResult:
    jd_source: str = ""
    jd_script: str = "unknown"
    block_script: Optional[str] = None        # script of the .tex block we rewrote
    selected: list = field(default_factory=list)   # list[(Bullet, score, matched)]
    coverage: float = 0.0
    new_tex: Optional[str] = None             # full tailored .tex text, or None
    notes: list = field(default_factory=list)

    def format_text(self) -> str:
        lines = []
        lines.append("Tailor (JD -> experience bank -> tailored variant)")
        lines.append(f"  JD script : {self.jd_script}")
        if self.block_script:
            lines.append(f"  block     : TAILOR BLOCK {self.block_script}")
        lines.append(f"  coverage  : {int(round(self.coverage * 100))}% of JD keywords "
                     f"present in the selected bullets")
        if self.notes:
            for n in self.notes:
                lines.append(f"  [note] {n}")
        if not self.selected:
            lines.append("  (no bullets selected)")
            return "\n".join(lines)
        lines.append(f"  selected {len(self.selected)} bullets (top matches):")
        for i, (b, score, matched) in enumerate(self.selected, 1):
            kw = ", ".join(matched[:6]) if matched else "—"
            lines.append(f"  {i}. [{score}] {b.text}")
            if matched:
                lines.append(f"       matched: {kw}")
        return "\n".join(lines)


def parse_experience_bank(text: str) -> list[Bullet]:
    """Parse ``docs/experience_bank.md`` into a flat list of :class:`Bullet`.

    Recognizes ``## Role: ...`` and ``## Personal open-source project: ...`` as
    role sections, ``#### Component: ...`` as sub-grouping, and ``- `` lines under
    a ``### Bullet material`` / ``### Bullets`` subsection as bullets. Code fences
    and ``### Context`` subsections are skipped. Works for any script because it
    only looks at list syntax, not Latin letters.
    """
    bullets: list[Bullet] = []
    in_fence = False
    current_role = ""
    current_component = ""
    in_bullet_section = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            low = title.lower()
            if low.startswith("role:") or low.startswith("personal open-source project"):
                current_role = title
                current_component = ""
                in_bullet_section = False
            else:
                current_role = ""          # Skills templates / How-to -> no bullets
                in_bullet_section = False
            continue
        if line.startswith("#### "):
            current_component = line[5:].strip()
            continue
        if line.startswith("### "):
            sub = line[4:].strip().lower()
            in_bullet_section = sub in ("bullet material", "bullets")
            continue
        if line.lstrip().startswith("- ") and current_role and in_bullet_section:
            bt = line.lstrip()[2:].strip()
            if bt:
                bullets.append(Bullet(text=bt, role=current_role, component=current_component))
    return bullets


def score_bullets(bullets: list[Bullet], jd_text: str) -> list[tuple[Bullet, int, list]]:
    """Return ``(bullet, score, matched_keywords)`` sorted by score descending.

    ``score`` = sum of JD keyword frequencies for tokens present in the bullet, so
    bullets containing many high-frequency JD terms rank highest. Uses
    ``script_aware_tokens`` so non-Latin JDs/bullets compare correctly.
    """
    jd_tokens = script_aware_tokens(jd_text)
    if not jd_tokens:
        return [(b, 0, []) for b in bullets]
    scored = []
    for b in bullets:
        bt = script_aware_tokens(b.text)
        matched = [t for t in jd_tokens if t in bt]
        score = sum(jd_tokens[t] for t in matched)
        scored.append((b, score, matched))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def _filter_by_script(bullets: list[Bullet], script: Script) -> list[Bullet]:
    if script is Script.UNKNOWN:
        return bullets
    return [b for b in bullets if detect_script(b.text) == script]


def select_bullets(scored: list, top_n: int = 8, per_role: int = 4, min_score: int = 1):
    """Group by role, take top ``per_role`` per role, then overall top ``top_n``.

    Only bullets with ``score >= min_score`` are eligible (no invented matches).
    If nothing scores, fall back to the top bullets by score (score 0) so the
    user still gets a starting set; ``fell_back`` flags this.
    """
    eligible = [s for s in scored if s[1] >= min_score]
    fell_back = False
    if not eligible:
        eligible = scored
        fell_back = True
    by_role: dict = {}
    for s in eligible:
        by_role.setdefault(s[0].role, []).append(s)
    chosen = []
    for items in by_role.values():
        chosen.extend(items[:per_role])
    chosen.sort(key=lambda x: x[1], reverse=True)
    return chosen[:top_n], fell_back


def _choose_block(base_text: str, jd_script: Script):
    """Return ``(block_script, inner_content)`` for the marker block matching
    ``jd_script``. Falls back to LATIN; returns ``(None, None)`` if no markers."""
    blocks = {m.group("tag"): m.group(2) for m in _MARKER_RE.finditer(base_text)}
    if not blocks:
        return None, None
    tag = _SCRIPT_TAG.get(jd_script)
    if tag in blocks:
        return _TAG_TO_SCRIPT[tag], blocks[tag]
    if "LATIN" in blocks:
        return Script.LATIN, blocks["LATIN"]
    first_tag = next(iter(blocks))
    return _TAG_TO_SCRIPT[first_tag], blocks[first_tag]


def tailor_variant(jd_text: str, bank_text: str, base_text: str = "",
                   top_n: int = 8, per_role: int = 4,
                   jd_source: str = "") -> TailorResult:
    """Core tailor logic (pure text in -> result). No file I/O.

    ``base_text`` is the base .tex content (empty string disables .tex rewrite;
    a snippet + report are still produced).
    """
    jd_script = detect_script(jd_text)
    bullets = parse_experience_bank(bank_text)
    res = TailorResult(jd_source=jd_source, jd_script=jd_script.value)

    block_script, _ = _choose_block(base_text, jd_script) if base_text else (None, None)
    if block_script is None:
        if base_text:
            res.notes.append("base .tex has no TAILOR BLOCK markers — "
                             "emitting snippet + report only (no .tex rewrite)")
        filtered = bullets
    else:
        res.block_script = block_script.value
        filtered = _filter_by_script(bullets, block_script)

    scored = score_bullets(filtered, jd_text)
    selected, fell_back = select_bullets(scored, top_n=top_n, per_role=per_role)
    res.selected = selected
    if fell_back:
        res.notes.append("no bullets matched JD keywords — included top bullets "
                         "as a starting set; review before sending")

    sel_text = " ".join(b.text for b, _, _ in selected)
    cov, _ = _keyword_coverage(sel_text, jd_text)
    res.coverage = cov

    if base_text and block_script is not None:
        res.new_tex = _substitute_block(base_text, jd_script, [b for b, _, _ in selected])
    return res


def _substitute_block(base_text: str, jd_script: Script, bullets: list[Bullet]) -> Optional[str]:
    """Replace the first matching marker block with the selected bullets."""
    block_script, _ = _choose_block(base_text, jd_script)
    if block_script is None:
        return None
    tag = _SCRIPT_TAG[block_script]
    items = "\n".join(f"  \\item {b.text}." for b in bullets)
    new_block = (
        f"% >>> TAILOR BLOCK {tag} START\n"
        f"\\begin{{itemize}}\n{items}\n\\end{{itemize}}\n"
        f"% >>> TAILOR BLOCK {tag} END"
    )
    return _MARKER_RE.sub(lambda m: new_block, base_text, count=1)


def _slug(s: str) -> str:
    s = (s or "jd").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "jd"


def run_tailor(jd_text: str, bank_text: str, base_tex: Optional[Path] = None,
               out_dir: Optional[Path] = None, top_n: int = 8, per_role: int = 4,
               jd_source: str = "") -> TailorResult:
    """File-aware wrapper: reads ``base_tex`` and writes outputs to ``out_dir``."""
    base_text = base_tex.read_text(encoding="utf-8") if base_tex else ""
    res = tailor_variant(jd_text, bank_text, base_text, top_n=top_n,
                          per_role=per_role, jd_source=jd_source)
    if out_dir is None:
        return res
    out_dir.mkdir(parents=True, exist_ok=True)

    # Always emit a paste-ready .tex snippet.
    snippet = "\n".join(f"  \\item {b.text}." for b, _, _ in res.selected)
    sp = out_dir / "tailored_bullets.tex"
    sp.write_text("\\begin{itemize}\n" + snippet + "\n\\end{itemize}\n", encoding="utf-8")
    res.notes.append(f"wrote snippet: {sp}")

    # Emit a full tailored .tex when the base has a rewritable block.
    if res.new_tex:
        target = out_dir / f"resume-jd-{_slug(jd_source)}.tex"
        target.write_text(res.new_tex, encoding="utf-8")
        res.notes.append(f"wrote tailored .tex: {target}")
    return res


__all__ = ["Bullet", "TailorResult", "parse_experience_bank", "score_bullets",
           "select_bullets", "tailor_variant", "run_tailor"]
