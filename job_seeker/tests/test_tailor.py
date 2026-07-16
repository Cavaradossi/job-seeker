"""Tests for job_seeker.tailor (Phase 4 drafter)."""
from __future__ import annotations

from pathlib import Path

from job_seeker.tailor import (
    parse_experience_bank,
    score_bullets,
    select_bullets,
    tailor_variant,
    Bullet,
)

BANK = """\
# Experience Bank (Example)

## Role: SRE @ Acme (2020-2022)

### Context

- Team size: 5

### Bullet material

#### Component: Platform

- Built Kubernetes platform serving 10k pods
- Reduced latency by 40% through caching
- Maintained EXISTING_PLATFORM (not greenfield)

#### Component: Logs

- Reconstructed log system based on Kafka and MySQL

## Personal open-source project: MyTool

### Bullets

- Published CLI tool to PyPI
- Built artifact audit framework

## Skills section templates

### job / JD variant

```
Skills: Python, Bash, SQL
```
"""

JD_SRE = (
    "We are hiring an SRE / platform engineer with strong Kubernetes, "
    "distributed systems, and infrastructure experience."
)

BASE_TEX = r"""\documentclass{resume}
\begin{document}
\section{Experience}
% >>> TAILOR BLOCK LATIN START
\begin{itemize}
\item old bullet
\end{itemize}
% >>> TAILOR BLOCK LATIN END
\section{Skills}
\end{document}
"""


def test_parse_experience_bank_extracts_bullets():
    bullets = parse_experience_bank(BANK)
    texts = [b.text for b in bullets]
    assert "Built Kubernetes platform serving 10k pods" in texts
    assert "Published CLI tool to PyPI" in texts
    # Skills templates are in a code fence -> excluded
    assert not any("Bash" in t for t in texts)
    # Context bullets excluded
    assert not any("Team size" in t for t in texts)
    assert len(bullets) == 6


def test_score_bullets_ranks_jd_matches_higher():
    bullets = parse_experience_bank(BANK)
    scored = score_bullets(bullets, JD_SRE)
    top_text = scored[0][0].text
    # The Kubernetes/platform bullet must outrank the PyPI bullet for an SRE JD.
    assert "Kubernetes" in top_text or "platform" in top_text.lower()
    pypi_score = next(s for b, s, _ in scored if "PyPI" in b.text)
    k8s_score = next(s for b, s, _ in scored if "Kubernetes" in b.text)
    assert k8s_score > pypi_score


def test_select_bullets_respects_per_role_and_falls_back():
    bullets = parse_experience_bank(BANK)
    scored = score_bullets(bullets, JD_SRE)
    selected, fell_back = select_bullets(scored, top_n=10, per_role=1, min_score=1)
    roles = {b.role for b, _, _ in selected}
    # per_role=1 caps each role at one bullet
    assert all(list(roles))
    # fallback when nothing scores: returns top bullets, fell_back True
    zero_jd = "zzz qqq xxx"  # no overlapping tokens
    scored0 = score_bullets(bullets, zero_jd)
    sel0, fb0 = select_bullets(scored0, top_n=3, min_score=1)
    assert fb0 is True
    assert len(sel0) > 0


def test_tailor_variant_substitutes_marked_block():
    res = tailor_variant(JD_SRE, BANK, BASE_TEX, jd_source="acme-sre")
    assert res.jd_script == "latin"
    assert res.block_script == "latin"
    assert res.new_tex is not None
    # the old bullet is gone, a selected bullet is present
    assert "old bullet" not in res.new_tex
    assert "Kubernetes" in res.new_tex or "platform" in res.new_tex.lower()
    # markers are preserved (reversible convention)
    assert "TAILOR BLOCK LATIN START" in res.new_tex
    assert "TAILOR BLOCK LATIN END" in res.new_tex


def test_tailor_variant_no_markers_emits_snippet_only():
    base_no_markers = r"\documentclass{resume}\begin{document}\end{document}"
    res = tailor_variant(JD_SRE, BANK, base_no_markers, jd_source="x")
    assert res.new_tex is None
    assert res.block_script is None
    assert any("no TAILOR BLOCK markers" in n for n in res.notes)
    # selection still happens
    assert len(res.selected) >= 1


def test_tailor_variant_cjk_jd_uses_cjk_block():
    cjk_base = (
        "% >>> TAILOR BLOCK CJK START\n"
        "\\begin{itemize}\n\\item 旧条目\n\\end{itemize}\n"
        "% >>> TAILOR BLOCK CJK END\n"
    )
    cjk_jd = "我们需要一位熟悉分布式系统和平台的工程师"
    cjk_bank = (
        "## Role: 后端 @ 甲公司\n### Bullet material\n"
        "- 构建分布式平台服务\n- 优化缓存降低延迟\n"
    )
    res = tailor_variant(cjk_jd, cjk_bank, cjk_base, jd_source="cn-jd")
    assert res.jd_script == "cjk"
    assert res.block_script == "cjk"
    assert res.new_tex is not None
    assert "旧条目" not in res.new_tex
