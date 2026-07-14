"""Adapter registry: pick a site adapter by URL host."""
from .base import SiteAdapter, JDText
from .workday_generic import GenericAdapter
from .boss_zhipin import BossZhipinAdapter
from .linkedin import LinkedInAdapter


def pick_adapter(url: str) -> SiteAdapter:
    """Return the adapter for a given URL (falls back to GenericAdapter)."""
    u = (url or "").lower()
    if "zhipin.com" in u or "boss.zhipin" in u:
        return BossZhipinAdapter()
    if "linkedin.com" in u:
        return LinkedInAdapter()
    return GenericAdapter()


__all__ = [
    "SiteAdapter", "JDText", "GenericAdapter",
    "BossZhipinAdapter", "LinkedInAdapter", "pick_adapter",
]
