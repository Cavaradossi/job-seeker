"""DOCX -> Markdown via pandoc.

Good fidelity for text content: headings, lists, emphasis, tables, and links
survive. Word-specific styling (text boxes, columns, exact fonts) does not
map to Markdown. Use this to turn an uploaded Word resume into an editable
Markdown source you can then convert onward.
"""
from .base import Adapter
from ..tools import resolve, env_with_tex


class DocxToMarkdown(Adapter):
    input_format = "docx"
    output_format = "md"
    lossy_note = (
        "Word-specific styling (text boxes, columns, exact fonts) is dropped; "
        "headings, lists, tables, and inline emphasis are preserved."
    )

    def convert(self, input_path: str, output_path: str) -> bool:
        pandoc = resolve("pandoc")
        if not pandoc:
            print("[DocxToMarkdown] pandoc not found. Install: brew install pandoc")
            return False
        self._ensure_parent(output_path)
        ok, out = self._run(
            [pandoc, "--from=docx", "--to=markdown", "--standalone",
             "-o", output_path, str(input_path)],
            env=env_with_tex(),
        )
        if not ok:
            print(f"[DocxToMarkdown] pandoc failed:\n{out[-1500:]}")
        return ok
