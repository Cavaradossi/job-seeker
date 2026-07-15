"""Render a resume variant: locate the .tex and compile to PDF (Phase 2 reuse).

Search order for the .tex: LaTeX_Resume_CN, LaTeX_Resume_EN, resume_template.
In the public template repo only resume_template/sample-resume-en_US-zh_CN.tex exists;
add your own variants to LaTeX_Resume_*/ in your private fork.
"""
from __future__ import annotations

from pathlib import Path

from convert.adapters.latex_to_pdf import LatexToPdf

ROOT = Path(__file__).resolve().parents[2]
VARIANT_DIRS = [
    ROOT / "LaTeX_Resume_CN",
    ROOT / "LaTeX_Resume_EN",
    ROOT / "resume_template",
]
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
