"""LaTeX -> Markdown via pandoc (LOSSY).

pandoc extracts the textual content of a LaTeX document into Markdown.
Custom resume macros (\\name, \\contactInfo, \\datedsubsection, \\fa*, ...)
and the resume.cls layout are NOT understood — you get section text and
bullets, not a faithful representation of the PDF. Use this to seed an
editable Markdown draft from an existing .tex, then hand-edit.
"""
from .base import Adapter
from ..tools import resolve, env_with_tex


class LatexToMarkdown(Adapter):
    input_format = "tex"
    output_format = "md"
    lossy_note = (
        "Custom resume macros (\\name/\\contactInfo/\\datedsubsection/\\fa*) "
        "and resume.cls layout are dropped; only textual content + bullets are "
        "extracted. Not a faithful mirror of the PDF."
    )

    def convert(self, input_path: str, output_path: str) -> bool:
        pandoc = resolve("pandoc")
        if not pandoc:
            print("[LatexToMarkdown] pandoc not found. Install: brew install pandoc")
            return False
        self._ensure_parent(output_path)
        ok, out = self._run(
            [pandoc, "--from=latex", "--to=markdown", "--standalone",
             "-o", output_path, str(input_path)],
            env=env_with_tex(),
        )
        if not ok:
            print(f"[LatexToMarkdown] pandoc failed:\n{out[-1500:]}")
        return ok
