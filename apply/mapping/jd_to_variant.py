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
from enum import Enum
from typing import List, Optional

from ..adapters.base import JDText


class Script(str, Enum):
    """Writing systems we treat as first-class (script-agnostic i18n)."""
    LATIN = "latin"
    CJK = "cjk"
    CYRILLIC = "cyrillic"
    ARABIC = "arabic"
    HEBREW = "hebrew"
    DEVANAGARI = "devanagari"
    GREEK = "greek"
    UNKNOWN = "unknown"


@dataclass
class VariantRecommendation:
    variant: str            # .tex stem, e.g. "resume_backend_ops"
    reason: str
    matched_keywords: List[str] = field(default_factory=list)
    warning: str = ""       # surfaced to the user when no native-script template exists


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


def detect_script(text: str) -> Script:
    """Detect the dominant writing system of `text` (script-agnostic).

    Counts codepoints per Unicode block rather than a Latin-vs-CJK binary, so
    Cyrillic / Arabic / Hebrew / Devanagari / Greek JDs are classified correctly
    instead of being silently forced to the Chinese variant.

    Latin is treated as a *fallback*: it only wins when no other script-specific
    characters are present, otherwise a mixed "Python и Kubernetes" sentence is
    correctly reported as Cyrillic (not Latin).
    """
    counts = {s: 0 for s in Script}
    for ch in text:
        if not ch.isalpha():
            continue
        cp = ord(ch)
        if 0x0400 <= cp <= 0x04FF:
            counts[Script.CYRILLIC] += 1
        elif (0x0600 <= cp <= 0x06FF or 0x0750 <= cp <= 0x077F
              or 0x08A0 <= cp <= 0x08FF or 0xFB50 <= cp <= 0xFDFF
              or 0xFE70 <= cp <= 0xFEFF):
            counts[Script.ARABIC] += 1
        elif 0x0590 <= cp <= 0x05FF:
            counts[Script.HEBREW] += 1
        elif 0x0900 <= cp <= 0x097F:
            counts[Script.DEVANAGARI] += 1
        elif 0x0370 <= cp <= 0x03FF or 0x1F00 <= cp <= 0x1FFF:
            counts[Script.GREEK] += 1
        elif (0x3000 <= cp <= 0x303F or 0x3400 <= cp <= 0x4DBF
              or 0x4E00 <= cp <= 0x9FFF or 0xF900 <= cp <= 0xFAFF
              or 0xFF00 <= cp <= 0xFFEF):
            counts[Script.CJK] += 1
        elif ch.isascii():
            counts[Script.LATIN] += 1
        else:
            counts[Script.UNKNOWN] += 1

    # Ignore LATIN when judging dominance: a non-Latin script must win even if the
    # text also contains Latin-script brand names / technical terms.
    candidates = {s: c for s, c in counts.items() if s is not Script.LATIN and c > 0}
    if not candidates:
        # Pure Latin (or empty) — Latin is the only signal.
        return Script.LATIN if counts[Script.LATIN] > 0 else Script.UNKNOWN
    best = max(candidates, key=lambda s: candidates[s])
    return best


def recommend_variant(jd: JDText, preferred_script: Optional[str] = None) -> VariantRecommendation:
    """Recommend a resume variant for the given JD. Never raises.

    `preferred_script` is the user's primary resume language (e.g. "en", "zh",
    "ru", "ar") — used as the fallback base when the JD's script has no native
    template shipped yet. We never silently force Chinese for non-Latin scripts;
    instead we pick the closest available base and set `warning`.
    """
    title = (getattr(jd, "title", "") or "").lower()
    body = (getattr(jd, "raw_text", "") or "").lower()
    blob = f"{title}\n{body}"

    for keywords, variant, reason in RULES:
        hit = [k for k in keywords if k in blob]
        if hit:
            return VariantRecommendation(variant=variant, reason=reason, matched_keywords=hit)

    # default: general 1-page variant, chosen by detected script (not EN/CN binary)
    script = detect_script(blob)
    if script is Script.CJK:
        return VariantRecommendation(
            variant="resume-zh_job",
            reason="no keyword match; CJK script → CN general (1 page)",
        )
    if script is Script.LATIN:
        return VariantRecommendation(
            variant="resume_job_en",
            reason="no keyword match; Latin script → EN general (1 page)",
        )

    # Non-Latin, non-CJK script (Cyrillic / Arabic / Hebrew / Devanagari / Greek
    # / unknown): no native-script template ships in the public repo. Use the
    # user's preferred base (default EN), and warn instead of forcing CN.
    pref = (preferred_script or "en").lower()
    base_is_en = pref not in ("zh", "cn", "chi", "chinese")
    variant = "resume_job_en" if base_is_en else "resume-zh_job"
    base_label = "EN" if base_is_en else "CN"
    return VariantRecommendation(
        variant=variant,
        reason=f"no keyword match; script '{script.value}' has no native template yet "
               f"— using {base_label} general as base",
        warning=f"JD script is '{script.value}', but no LaTeX_Resume_"
                f"{script.value.upper()} template ships yet. Using the {base_label} "
                f"general variant as a base — add your own LaTeX_Resume_<SCRIPT>/ "
                f"for native rendering (see SKILL §6).",
    )
