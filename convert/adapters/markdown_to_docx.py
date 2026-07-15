"""Markdown -> DOCX via pandoc.

High fidelity for standard Markdown: headings, lists, emphasis, tables, and
links map cleanly to Word styles. Use this to hand an editable Word file to
someone who does not use LaTeX/Markdown.
"""
from .base import Adapter
from ..tools import resolve, env_with_tex


class MarkdownToDocx(Adapter):
    input_format = "md"
    output_format = "docx"
    lossy_note = None

    def convert(self, input_path: str, output_path: str) -> bool:
        pandoc = resolve("pandoc")
        if not pandoc:
            print("[MarkdownToDocx] pandoc not found. Install: brew install pandoc")
            return False
        self._ensure_parent(output_path)
        ok, out = self._run(
            [pandoc, "--from=markdown", "--to=docx",
             "-o", output_path, str(input_path)],
            env=env_with_tex(),
        )
        if not ok:
            print(f"[MarkdownToDocx] pandoc failed:\n{out[-1500:]}")
        return ok
