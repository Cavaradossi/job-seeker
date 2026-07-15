"""Chain adapters with temp intermediates + auto-route by file extension.

Each adapter declares (input_format, output_format). `route()` does BFS over
the direct adapter edges, preferring the shortest chain (direct edges first).
`Pipeline` threads temp files between adapters.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from collections import deque
from pathlib import Path
from typing import List

from .adapters import (
    MarkdownToLatex, LatexToPdf, LatexToDocx, DocxToLatex, MarkdownToPdf,
    MarkdownToDocx, DocxToMarkdown, DocxToPdf, LatexToMarkdown, PdfToMarkdown,
)
from .adapters.base import Adapter


# Direct adapter edges: (in_ext, out_ext) -> Adapter class.
# With these 10 direct edges, BFS reaches every ordered pair among the four
# formats (md / tex / docx / pdf). PDF is input-only (via PyMuPDF); PDF -> tex
# and PDF -> docx route through PDF -> md.
_EDGES = {
    ("md", "tex"): MarkdownToLatex,
    ("md", "pdf"): MarkdownToPdf,
    ("md", "docx"): MarkdownToDocx,
    ("tex", "pdf"): LatexToPdf,
    ("tex", "docx"): LatexToDocx,
    ("tex", "md"): LatexToMarkdown,
    ("docx", "tex"): DocxToLatex,
    ("docx", "md"): DocxToMarkdown,
    ("docx", "pdf"): DocxToPdf,
    ("pdf", "md"): PdfToMarkdown,
}


def _ext(path: str) -> str:
    return Path(path).suffix.lower().lstrip(".")


def route(input_path: str, output_path: str) -> List[Adapter]:
    """Return adapter instances connecting input ext -> output ext (shortest path).

    Raises ValueError if no route exists. Returns [] when src == dst.
    """
    src, dst = _ext(input_path), _ext(output_path)
    if src == dst:
        return []
    q = deque([(src, [])])
    seen = {src}
    while q:
        node, path = q.popleft()
        for (a, b), cls in _EDGES.items():
            if a == node and b not in seen:
                new_path = path + [cls()]
                if b == dst:
                    return new_path
                seen.add(b)
                q.append((b, new_path))
    raise ValueError(
        f"No conversion route from .{src} to .{dst}. "
        f"Supported edges: {sorted(f'{a}->{b}' for a, b in _EDGES)}"
    )


class Pipeline:
    """Run a sequence of adapters, threading temp files between them.

        Pipeline(MarkdownToLatex(), LatexToPdf()).run("in.md", "out.pdf")
        Pipeline.auto("in.md", "out.pdf")   # auto-route by extension
    """

    def __init__(self, *adapters: Adapter):
        if not adapters:
            raise ValueError("Pipeline requires at least one adapter")
        self.adapters: List[Adapter] = list(adapters)

    def run(self, input_path: str, output_path: str) -> bool:
        ads = self.adapters
        if len(ads) == 1:
            return ads[0].convert(input_path, output_path)
        tmpdir = tempfile.mkdtemp(prefix="jobseeker_convert_")
        try:
            current = input_path
            for i, ad in enumerate(ads[:-1]):
                tmp_out = os.path.join(tmpdir, f"step{i}.{ad.output_format}")
                if not ad.convert(current, tmp_out):
                    return False
                current = tmp_out
            return ads[-1].convert(current, output_path)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    @staticmethod
    def auto(input_path: str, output_path: str) -> bool:
        adapters = route(input_path, output_path)
        if not adapters:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(input_path, output_path)
            return True
        return Pipeline(*adapters).run(input_path, output_path)
