"""Adapter registry: pick a site adapter by URL host.

Routing is now data-driven (see ``registry.py`` + ``portals.yaml``). ``pick_adapter``
keeps its old signature for backward compatibility but delegates to the registry.
"""
from .base import SiteAdapter, JDText
from .workday_generic import GenericAdapter
from .boss_zhipin import BossZhipinAdapter
from .linkedin import LinkedInAdapter
from .registry import (
    resolve_adapter, load_adapter, resolve, recommend_platforms, add_portal,
)


def pick_adapter(url: str) -> SiteAdapter:
    """Return the adapter for a given URL (falls back to GenericAdapter)."""
    return resolve(url)[0]


__all__ = [
    "SiteAdapter", "JDText", "GenericAdapter",
    "BossZhipinAdapter", "LinkedInAdapter", "pick_adapter",
    "resolve_adapter", "load_adapter", "resolve",
    "recommend_platforms", "add_portal",
]
