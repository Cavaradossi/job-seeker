"""Render a resume variant: locate the .tex and compile to PDF (Phase 2 reuse).

Search order for the .tex: every LaTeX_Resume_<SCRIPT> dir (script-tagged, e.g.
CN, EN, RU, AR, HE, …), then resume_template as the final fallback. In the
public template repo only resume_template/sample-resume-en_US-zh_CN.tex exists;
add your own variants to LaTeX_Resume_*/ in your private fork — no code edits
needed, every writing system is discovered automatically.
"""
from __future__ import annotations

from pathlib import Path

from convert.adapters.latex_to_pdf import LatexToPdf

ROOT = Path(__file__).resolve().parents[2]


def _discover_variant_dirs() -> list:
    """All LaTeX_Resume_<SCRIPT> dirs (script-tagged, alphabetically), with
    resume_template appended as the final fallback.

    This makes any writing system's private variant buildable without touching
    code: drop a LaTeX_Resume_RU/ (or _AR, _HE, …) next to resume_template/ and
    it is picked up automatically.
    """
    dirs = sorted(
        (p for p in ROOT.glob("LaTeX_Resume_*") if p.is_dir()),
        key=lambda p: p.name,
    )
    dirs.append(ROOT / "resume_template")
    return dirs


VARIANT_DIRS = _discover_variant_dirs()
OUT = ROOT / "outputs"


def find_variant_tex(variant: str) -> Path:
    """Resolve a variant name/path to an existing .tex file."""
    p = Path(variant).expanduser()
    if p.is_absolute() and p.is_file():
        return p.resolve()
    if p.is_file():
        return p.resolve()

    stem = variant[:-4] if variant.endswith(".tex") else variant
    for d in VARIANT_DIRS:
        if not d.is_dir():
            continue
        for cand in (d / f"{stem}.tex", d / f"{variant}.tex", d / variant):
            if cand.is_file():
                return cand.resolve()
    raise FileNotFoundError(
        f"variant .tex not found for '{variant}' "
        f"(searched: {[str(d) for d in VARIANT_DIRS if d.is_dir()]})"
    )


def render_variant(variant: str, out_name: str | None = None) -> Path:
    """Compile the variant .tex to a PDF in outputs/ and return its path."""
    tex = find_variant_tex(variant)
    stem = out_name or f"{tex.stem}_applied"
    out = OUT / f"{stem}.pdf"
    OUT.mkdir(parents=True, exist_ok=True)
    ok = LatexToPdf().convert(str(tex), str(out))
    if not ok:
        raise RuntimeError(f"failed to compile variant: {tex}")
    return out
