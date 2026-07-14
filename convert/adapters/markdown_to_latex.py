"""Markdown -> LaTeX via pandoc.

pandoc MD->LaTeX is high fidelity for standard Markdown. With --standalone it
emits a full article-class document (NOT a resume.cls source). Use this to
draft editable LaTeX from Markdown notes; the curated .tex in
resume_template/ remains the PDF source of truth.
"""
from .base import Adapter
from ..tools import resolve, env_with_tex


class MarkdownToLatex(Adapter):
    input_format = "md"
    output_format = "tex"
    lossy_note = None

    def convert(self, input_path: str, output_path: str) -> bool:
        pandoc = resolve("pandoc")
        if not pandoc:
            print("[MarkdownToLatex] pandoc not found. Install: brew install pandoc")
            return False
        self._ensure_parent(output_path)
        ok, out = self._run(
            [pandoc, "--from=markdown", "--to=latex", "--standalone",
             "-o", output_path, str(input_path)],
            env=env_with_tex(),
        )
        if not ok:
            print(f"[MarkdownToLatex] pandoc failed:\n{out[-1500:]}")
        return ok
