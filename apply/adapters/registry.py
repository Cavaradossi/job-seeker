"""Portal registry: route a JD URL to a config + adapter, driven by portals.yaml.

The registry is **data, not code** — adding a platform means editing
``apply/portals.yaml`` (or running ``python -m apply --add-portal <url>``), not
writing a Python adapter. This keeps the extension bar low and the architecture
clean (the competitor's hard-coded per-site adapters are the anti-pattern we
avoid).

Public API
----------
* ``resolve_adapter(url)``  -> portal dict (id/name/url_patterns/regions/
  tos_blocks_automation/adapter) or a generic fallback.
* ``load_adapter(key)``     -> a *factory* returning a SiteAdapter instance for
  the adapter key (``generic`` / ``boss_zhipin`` / ``linkedin`` / ...).
* ``recommend_platforms(region)`` -> list of portal dicts serving ``region``.
* ``add_portal(url, name=None)``  -> new portal dict (does NOT write the file;
  the CLI prints it / optionally appends).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml  # PyYAML — config format; already in requirements.txt

from .base import SiteAdapter
from .workday_generic import GenericAdapter
from .boss_zhipin import BossZhipinAdapter
from .linkedin import LinkedInAdapter

PORTALS_PATH = Path(__file__).resolve().parent.parent / "portals.yaml"

# adapter key -> factory. New adapters register themselves here.
_ADAPTERS = {
    "generic": GenericAdapter,
    "boss_zhipin": BossZhipinAdapter,
    "linkedin": LinkedInAdapter,
}


def _load_portals(path: Optional[Path] = None) -> list:
    p = path or PORTALS_PATH
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return data.get("platforms", []) or []


def resolve_adapter(url: str, portals: Optional[list] = None) -> dict:
    """Return the portal config whose ``url_patterns`` match ``url``.

    Falls back to a generic portal dict when nothing matches (so callers always
    get a usable config with ``adapter: "generic"``).
    """
    u = (url or "").lower()
    for portal in (portals or _load_portals()):
        for pat in portal.get("url_patterns", []):
            if pat.lower() in u:
                return portal
    return {
        "id": "unknown",
        "name": "Generic ATS",
        "url_patterns": [],
        "regions": ["global"],
        "tos_blocks_automation": False,
        "adapter": "generic",
    }


def load_adapter(key: str) -> SiteAdapter:
    """Instantiate the adapter for a portal's ``adapter`` key."""
    factory = _ADAPTERS.get(key, GenericAdapter)
    return factory()


def resolve(url: str) -> tuple[SiteAdapter, dict]:
    """Convenience: (adapter_instance, portal_dict) for ``url``."""
    portal = resolve_adapter(url)
    return load_adapter(portal["adapter"]), portal


def recommend_platforms(region: str, portals: Optional[list] = None) -> list:
    """Return portals whose ``regions`` include ``region`` (case-insensitive)."""
    region = (region or "").upper()
    out = []
    for portal in (portals or _load_portals()):
        regions = [r.upper() for r in portal.get("regions", [])]
        if region in regions or "GLOBAL" in regions:
            out.append(portal)
    return out


def _host_of(url: str) -> str:
    m = re.search(r"https?://([^/\s]+)", url or "")
    return m.group(1).lower() if m else (url or "").lower()


def add_portal(url: str, name: Optional[str] = None) -> dict:
    """Build a new portal dict for ``url`` (does not persist — CLI handles that).

    The adapter key defaults to ``generic``; only ``boss_zhipin`` / ``linkedin``
    get a dedicated adapter, which the caller can override after review.
    """
    host = _host_of(url)
    clean = host.split(".")[-2] if "." in host else host
    pid = re.sub(r"[^a-z0-9]", "_", clean).strip("_") or "portal"
    return {
        "id": pid,
        "name": name or host,
        "url_patterns": [host],
        "regions": ["global"],
        "tos_blocks_automation": False,
        "adapter": "generic",
    }


__all__ = [
    "resolve_adapter", "load_adapter", "resolve", "recommend_platforms",
    "add_portal", "PORTALS_PATH",
]
