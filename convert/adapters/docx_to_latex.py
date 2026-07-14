"""DOCX -> LaTeX via pandoc (LOSSY).

Round-tripping through pandoc will NOT reproduce a resume.cls document.
Use this only to seed a new editable draft from an existing DOCX, then
hand-edit. Never overwrite a curated .tex from a DOCX round-trip.
"""
from .base import Adapter
from ..tools import resolve, env_with_tex


class DocxToLatex(Adapter):
    input_format = "docx"
    output_format = "tex"
    lossy_note = (
        "Produces a generic article-class LaTeX document, not a resume.cls "
        "source. Styling, columns, and icons are lost."
    )

    def convert(self, input_path: str, output_path: str) -> bool:
        pandoc = resolve("pandoc")
        if not pandoc:
            print("[DocxToLatex] pandoc not found. Install: brew install pandoc")
            return False
        self._ensure_parent(output_path)
        ok, out = self._run(
            [pandoc, "--from=docx", "--to=latex", "--standalone",
             "-o", output_path, str(input_path)],
            env=env_with_tex(),
        )
        if not ok:
            print(f"[DocxToLatex] pandoc failed:\n{out[-1500:]}")
        return ok
