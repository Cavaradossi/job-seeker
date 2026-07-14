"""Integration tests for the convert pipeline.

Uses the public sample resume_template/HouJP-en_US-zh_CN.tex. Tests that need
pandoc / xelatex are skipped (not failed) when those tools are absent, so the
suite stays green on a minimal CI runner.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from convert.tools import resolve
from convert.adapters.latex_to_pdf import LatexToPdf
from convert.adapters.latex_to_docx import LatexToDocx
from convert.pipeline import Pipeline, route

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_TEX = ROOT / "resume_template" / "HouJP-en_US-zh_CN.tex"

HAS_PANDOC = resolve("pandoc") is not None
HAS_XELATEX = resolve("xelatex") is not None

pytestmark = pytest.mark.skipif(not SAMPLE_TEX.exists(),
                                reason="sample tex not found")


def test_route_tex_to_pdf():
    ads = route(str(SAMPLE_TEX), "out.pdf")
    assert len(ads) == 1
    assert isinstance(ads[0], LatexToPdf)


def test_route_md_to_pdf_prefers_direct_edge():
    # md->pdf has a direct edge; route should pick it (1 hop, not 2).
    ads = route("in.md", "out.pdf")
    assert len(ads) == 1
    assert ads[0].input_format == "md" and ads[0].output_format == "pdf"


def test_route_md_to_docx_is_two_hop():
    # no direct md->docx edge; should go md->tex->docx (2 hops).
    ads = route("in.md", "out.docx")
    assert len(ads) == 2
    assert ads[0].input_format == "md"
    assert ads[-1].output_format == "docx"


def test_route_docx_to_pdf_is_two_hop():
    # docx->tex->pdf
    ads = route("in.docx", "out.pdf")
    assert len(ads) == 2


def test_route_unsupported_raises():
    with pytest.raises(ValueError):
        route("in.xyz", "out.pdf")


def test_pipeline_requires_adapter():
    with pytest.raises(ValueError):
        Pipeline()


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
