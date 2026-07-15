"""Integration tests for the convert pipeline.

Uses the public sample resume_template/sample-resume-en_US-zh_CN.tex. Tests that need
pandoc / xelatex / PyMuPDF are skipped (not failed) when those are absent, so the
suite stays green on a minimal CI runner.

The pipeline is any-to-any across four formats (tex / md / docx / pdf): ten direct
adapter edges cover all 12 ordered pairs, with BFS routing chaining the rest.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from convert.tools import resolve
from convert.adapters.latex_to_pdf import LatexToPdf
from convert.adapters.latex_to_docx import LatexToDocx
from convert.pipeline import Pipeline, route

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_TEX = ROOT / "resume_template" / "sample-resume-en_US-zh_CN.tex"

HAS_PANDOC = resolve("pandoc") is not None
HAS_XELATEX = resolve("xelatex") is not None

try:
    import fitz  # noqa: F401  (PyMuPDF)
    HAS_PYMUPDF = True
except Exception:  # pragma: no cover - import guard
    HAS_PYMUPDF = False

pytestmark = pytest.mark.skipif(not SAMPLE_TEX.exists(),
                                reason="sample tex not found")


# --- routing (no external tools needed) ------------------------------------

def test_route_tex_to_pdf():
    ads = route(str(SAMPLE_TEX), "out.pdf")
    assert len(ads) == 1
    assert isinstance(ads[0], LatexToPdf)


def test_route_md_to_pdf_prefers_direct_edge():
    ads = route("in.md", "out.pdf")
    assert len(ads) == 1
    assert ads[0].input_format == "md" and ads[0].output_format == "pdf"


def test_route_md_to_docx_is_direct():
    # md->docx now has a direct edge (was two-hop before v0.3).
    ads = route("in.md", "out.docx")
    assert len(ads) == 1
    assert ads[0].input_format == "md" and ads[0].output_format == "docx"


def test_route_docx_to_pdf_is_direct():
    # docx->pdf now has a direct edge (was two-hop before v0.3).
    ads = route("in.docx", "out.pdf")
    assert len(ads) == 1
    assert ads[0].input_format == "docx" and ads[0].output_format == "pdf"


def test_route_tex_to_md_is_direct():
    ads = route(str(SAMPLE_TEX), "out.md")
    assert len(ads) == 1
    assert ads[0].input_format == "tex" and ads[0].output_format == "md"


def test_route_pdf_to_md_is_direct():
    ads = route("in.pdf", "out.md")
    assert len(ads) == 1
    assert ads[0].input_format == "pdf" and ads[0].output_format == "md"


def test_route_pdf_to_tex_chains_via_md():
    # no direct pdf->tex edge; BFS routes pdf->md->tex.
    ads = route("in.pdf", "out.tex")
    assert len(ads) == 2
    assert ads[0].input_format == "pdf" and ads[0].output_format == "md"
    assert ads[-1].output_format == "tex"


def test_route_pdf_to_docx_chains_via_md():
    ads = route("in.pdf", "out.docx")
    assert len(ads) == 2
    assert ads[0].input_format == "pdf"
    assert ads[-1].output_format == "docx"


def test_every_ordered_pair_is_routable():
    # All 12 ordered pairs among the 4 formats must resolve to >=1 adapter.
    formats = ["tex", "md", "docx", "pdf"]
    for src in formats:
        for dst in formats:
            if src == dst:
                continue
            ads = route(f"in.{src}", f"out.{dst}")
            assert ads, f"no route for {src}->{dst}"


def test_route_unsupported_raises():
    with pytest.raises(ValueError):
        route("in.xyz", "out.pdf")


def test_pipeline_requires_adapter():
    with pytest.raises(ValueError):
        Pipeline()


# --- real conversions (skip when tools missing) ----------------------------

@pytest.mark.skipif(not HAS_XELATEX, reason="xelatex not installed")
def test_latex_to_pdf_real(tmp_path):
    out = tmp_path / "sample.pdf"
    ok = LatexToPdf().convert(str(SAMPLE_TEX), str(out))
    assert ok, "xelatex compilation failed (see stdout)"
    assert out.exists() and out.stat().st_size > 1000


@pytest.mark.skipif(not HAS_PANDOC, reason="pandoc not installed")
def test_latex_to_docx_real(tmp_path):
    out = tmp_path / "sample.docx"
    ok = LatexToDocx().convert(str(SAMPLE_TEX), str(out))
    assert ok, "pandoc latex->docx failed"
    assert out.exists() and out.stat().st_size > 1000


@pytest.mark.skipif(not HAS_PANDOC, reason="pandoc not installed")
def test_latex_to_markdown_real(tmp_path):
    out = tmp_path / "sample.md"
    ok = Pipeline.auto(str(SAMPLE_TEX), str(out))
    assert ok, "pandoc latex->md failed"
    assert out.exists() and out.read_text(encoding="utf-8").strip()


@pytest.mark.skipif(not HAS_PANDOC, reason="pandoc not installed")
def test_markdown_to_docx_real(tmp_path):
    md = tmp_path / "in.md"
    md.write_text("# Jane Doe\n\n## Experience\n\n- one\n- two\n", encoding="utf-8")
    out = tmp_path / "out.docx"
    ok = Pipeline.auto(str(md), str(out))
    assert ok
    assert out.exists() and out.stat().st_size > 1000


@pytest.mark.skipif(not (HAS_XELATEX and HAS_PANDOC), reason="needs xelatex+pandoc")
def test_docx_to_pdf_real(tmp_path):
    # Build a docx first (md->docx), then docx->pdf.
    md = tmp_path / "in.md"
    md.write_text("# Jane Doe\n\nA test resume draft.\n", encoding="utf-8")
    docx = tmp_path / "mid.docx"
    assert Pipeline.auto(str(md), str(docx))
    out = tmp_path / "out.pdf"
    ok = Pipeline.auto(str(docx), str(out))
    assert ok
    assert out.exists() and out.stat().st_size > 1000


@pytest.mark.skipif(not (HAS_XELATEX and HAS_PYMUPDF), reason="needs xelatex+PyMuPDF")
def test_pdf_to_markdown_real(tmp_path):
    # Compile the sample to PDF, then extract text back to markdown.
    pdf = tmp_path / "sample.pdf"
    assert LatexToPdf().convert(str(SAMPLE_TEX), str(pdf))
    out = tmp_path / "out.md"
    ok = Pipeline.auto(str(pdf), str(out))
    assert ok
    text = out.read_text(encoding="utf-8")
    assert "YOUR_NAME" in text  # placeholder name survives text extraction


@pytest.mark.skipif(not (HAS_XELATEX and HAS_PANDOC), reason="needs xelatex+pandoc")
def test_pipeline_md_to_pdf_real(tmp_path):
    md = tmp_path / "in.md"
    md.write_text(
        "# Jane Doe\n\nA **test** resume draft.\n\n"
        "## Experience\n\n- bullet one\n- bullet two\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.pdf"
    ok = Pipeline.auto(str(md), str(out))
    assert ok
    assert out.exists() and out.stat().st_size > 1000
