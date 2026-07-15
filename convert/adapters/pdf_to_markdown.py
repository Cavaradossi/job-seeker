"""PDF -> Markdown via PyMuPDF (LOSSY).

pandoc cannot read PDF, so PDF ingestion is handled here with PyMuPDF
(`import fitz`). We extract the text layer page by page and emit plain
Markdown. This is the entry point that makes *any* uploaded resume (incl.
PDF) convertible to the other formats via PDF -> MD -> {tex,docx,pdf}.

Lossiness is inherent: a PDF stores glyphs and positions, not semantic
structure. Headings, columns, tables, bullets, fonts, and icons are NOT
reliably recovered — you get the readable text in reading order. Always
review and re-structure the Markdown before converting onward.

Scanned/image-only PDFs have no text layer; OCR is out of scope (the
adapter returns False with a clear message).
"""
from .base import Adapter


class PdfToMarkdown(Adapter):
    input_format = "pdf"
    output_format = "md"
    lossy_note = (
        "PDF has no semantic structure — only text + positions are extracted. "
        "Headings, columns, tables, bullets, fonts, and icons are not reliably "
        "recovered; review the Markdown before converting onward. Scanned "
        "(image-only) PDFs yield no text (OCR is out of scope)."
    )

    def convert(self, input_path: str, output_path: str) -> bool:
        try:
            import fitz  # PyMuPDF
        except ImportError:
            print("[PdfToMarkdown] PyMuPDF not found. Install: pip install pymupdf")
            return False

        self._ensure_parent(output_path)
        try:
            doc = fitz.open(str(input_path))
        except Exception as e:  # noqa: BLE001 - report and fail gracefully
            print(f"[PdfToMarkdown] cannot open PDF: {e}")
            return False

        chunks = []
        total_text = 0
        try:
            for page in doc:
                text = page.get_text("text") or ""
                total_text += len(text.strip())
                chunks.append(text.rstrip())
        finally:
            doc.close()

        if total_text == 0:
            print("[PdfToMarkdown] no extractable text (likely a scanned/"
                  "image-only PDF). OCR is out of scope.")
            return False

        # Join pages with a horizontal rule so page breaks stay visible.
        body = "\n\n---\n\n".join(c for c in chunks if c.strip())
        header = ("<!-- Converted from PDF by job-seeker (PyMuPDF). "
                  "Text-only extraction; review and re-structure before use. -->\n\n")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(header + body + "\n")
        except OSError as e:
            print(f"[PdfToMarkdown] cannot write output: {e}")
            return False
        return True
