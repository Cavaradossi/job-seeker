"""Variant mapping (§3): JD keywords -> recommended resume variant (rule-based)."""
from .jd_to_variant import recommend_variant, VariantRecommendation, RULES
from .variant_renderer import render_variant, find_variant_tex

__all__ = [
    "recommend_variant", "VariantRecommendation", "RULES",
    "render_variant", "find_variant_tex",
]
