"""Markdown -> PDF via pandoc + xelatex (direct).

pandoc invokes xelatex as its PDF engine using pandoc's default LaTeX
template (article class) — this is NOT a resume layout.

CJK note: pandoc's default template uses Latin fonts. For CJK Markdown
supply a custom template or `--variable CJKmainfont=<font>`. For the
resume workflow, prefer the .tex -> .pdf path (LatexToPdf) which already
ships bundled CJK fonts in resume_template/fonts/.
"""
from .base import Adapter
from ..tools import resolve, env_with_tex


class MarkdownToPdf(Adapter):
    input_format = "md"
    output_format = "pdf"
    lossy_note = (
        "Uses pandoc's default LaTeX template (article class). Not a resume "
        "layout. For resume PDFs use .tex -> .pdf."
    )

    def convert(self, input_path: str, output_path: str) -> bool:
        pandoc = resolve("pandoc")
        if not pandoc:
            print("[MarkdownToPdf] pandoc not found. Install: brew install pandoc")
            return False
        if not resolve("xelatex"):
            print("[MarkdownToPdf] xelatex not found (pandoc PDF engine). See doc/BUILD_MAC.md.")
            return False
        self._ensure_parent(output_path)
        ok, out = self._run(
            [pandoc, "--from=markdown", "--to=pdf",
             "--pdf-engine=xelatex",
             "-o", output_path, str(input_path)],
            env=env_with_tex(),
        )
        if not ok:
            print(f"[MarkdownToPdf] pandoc failed:\n{out[-1500:]}")
        return ok
