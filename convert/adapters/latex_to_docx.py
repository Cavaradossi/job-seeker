"""LaTeX -> DOCX via pandoc (LOSSY).

pandoc does not understand custom resume macros (\\name, \\centerline,
\\contactInfo, \\datedsubsection, \\datedline, \\faGraduationCap, \\nth, ...).
The DOCX will be structurally approximate: section text and itemize bullets
survive, but custom layout, fonts, icons, and column geometry do not.

Treat the DOCX as an editable text mirror — never as a layout-accurate
rendering of the PDF. The .tex -> .pdf path is the source of truth.
"""
from .base import Adapter
from ..tools import resolve, env_with_tex


class LatexToDocx(Adapter):
    input_format = "tex"
    output_format = "docx"
    lossy_note = (
        "Custom resume macros (\\name/\\centerline/\\contactInfo/"
        "\\datedsubsection/\\datedline/\\nth/\\fa*) are dropped or flattened. "
        "Layout, fonts, and icons do not survive; text + bullets are approximate."
    )

    def convert(self, input_path: str, output_path: str) -> bool:
        pandoc = resolve("pandoc")
        if not pandoc:
            print("[LatexToDocx] pandoc not found. Install: brew install pandoc")
            return False
        self._ensure_parent(output_path)
        ok, out = self._run(
            [pandoc, "--from=latex", "--to=docx",
             "-o", output_path, str(input_path)],
            env=env_with_tex(),
        )
        if not ok:
            print(f"[LatexToDocx] pandoc failed:\n{out[-1500:]}")
        return ok
