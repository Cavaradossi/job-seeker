"""Rule-based JD -> resume variant recommendation (§3).

First-match-wins over an ordered keyword list. Returns a variant NAME (the
.tex stem, matching the SKILL §3 variant table). The renderer then tries to
locate the .tex in LaTeX_Resume_CN / LaTeX_Resume_EN / resume_template.

In the public template repo only the upstream sample (sample-resume-en_US-zh_CN)
exists; users add their own variants to LaTeX_Resume_*/. The recommender
still returns the right NAME so the workflow is correct once variants exist.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ..adapters.base import JDText


@dataclass
class VariantRecommendation:
    variant: str            # .tex stem, e.g. "resume_backend_ops"
    reason: str
    matched_keywords: List[str] = field(default_factory=list)


# Ordered rules: (keywords, variant_stem, reason). First match wins.
RULES = [
    (["backend", "sre", "ops", "devops", "infrastructure", "kubernetes",
      "site reliability", "platform engineer", "systems engineer"],
     "resume_backend_ops", "backend / SRE / ops keywords"),
    (["ai", "llm", "rag", "eval", "benchmark", "machine learning", "ml",
      "model", "inference", "nlp", "deep learning"],
     "resume_ai_eval", "AI / LLM / eval keywords"),
    (["web3", "crypto", "blockchain", "solidity", "ethereum", "defi",
      "smart contract"],
     "resume_web3", "Web3 / crypto keywords"),
]


def _looks_english(text: str) -> bool:
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    asc = sum(1 for c in text if c.isascii() and c.isalpha())
    return asc > cjk


def recommend_variant(jd: JDText) -> VariantRecommendation:
    """Recommend a resume variant for the given JD. Never raises."""
    title = (getattr(jd, "title", "") or "").lower()
    body = (getattr(jd, "raw_text", "") or "").lower()
    blob = f"{title}\n{body}"

    for keywords, variant, reason in RULES:
        hit = [k for k in keywords if k in blob]
        if hit:
            return VariantRecommendation(variant=variant, reason=reason, matched_keywords=hit)

    # default: general 1-page variant, EN or CN by language heuristic
    if _looks_english(blob):
        return VariantRecommendation(
            variant="resume_job_en",
            reason="no keyword match; default EN general (1 page)",
        )
    return VariantRecommendation(
        variant="resume-zh_job",
        reason="no keyword match; default CN general (1 page)",
    )
