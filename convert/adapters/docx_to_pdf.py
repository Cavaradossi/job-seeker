"""DOCX -> PDF via pandoc + xelatex (LOSSY layout).

pandoc reads the DOCX content and re-typesets it through its default LaTeX
template (article class) with xelatex. The result is a clean, readable PDF
but NOT a pixel-match of how Word would render the same file — Word-specific
layout (text boxes, columns, exact fonts) is re-flowed.

For CJK content, pandoc's default template uses Latin fonts; supply a custom
template or CJK mainfont if needed. For resume-quality PDFs, prefer editing
the .tex and using .tex -> .pdf.
"""
from .base import Adapter
from ..tools import resolve, env_with_tex


class DocxToPdf(Adapter):
    input_format = "docx"
    output_format = "pdf"
    lossy_note = (
        "Re-typeset through pandoc's default LaTeX template (article class), "
        "not a Word-accurate rendering. Word layout (text boxes/columns/fonts) "
        "is re-flowed. For resume PDFs use .tex -> .pdf."
    )

    def convert(self, input_path: str, output_path: str) -> bool:
        pandoc = resolve("pandoc")
        if not pandoc:
            print("[DocxToPdf] pandoc not found. Install: brew install pandoc")
            return False
        if not resolve("xelatex"):
            print("[DocxToPdf] xelatex not found (pandoc PDF engine). See docs/BUILD_MAC.md.")
            return False
        self._ensure_parent(output_path)
        ok, out = self._run(
            [pandoc, "--from=docx", "--to=pdf",
             "--pdf-engine=xelatex",
             "-o", output_path, str(input_path)],
            env=env_with_tex(),
        )
        if not ok:
            print(f"[DocxToPdf] pandoc failed:\n{out[-1500:]}")
        return ok
