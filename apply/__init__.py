"""job-seeker browser-assisted application (Phase 3).

Read a JD URL -> recommend a resume variant -> prefill the application form
-> PAUSE for human confirmation -> submit -> record to tracker.

Iron rule (§3.1): `submit()` ALWAYS calls `confirm()` and blocks on its
return value before doing anything destructive. It never auto-submits.
"""
from .mapping.jd_to_variant import recommend_variant, VariantRecommendation
from .mapping.variant_renderer import render_variant, find_variant_tex
from .audit import log_event

__all__ = [
    "recommend_variant", "VariantRecommendation",
    "render_variant", "find_variant_tex",
    "log_event",
]
__version__ = "0.1.0"
