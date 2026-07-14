"""Site adapter ABC (§3.2 — one adapter per recruiting site).

Three responsibilities:
  - read_jd(url)      -> JDText     (HTTP fetch + parse; no login, no browser)
  - prefill_form(...) -> bool       (browser automation; fills fields, NEVER submits)
  - submit(...)       -> bool       (MUST call confirm() first; never auto-submits)

ToS compliance (§3.4): adapters whose site ToS prohibit automated form
interaction set `tos_blocks_automation = True`; the CLI then degrades to
"open page + show prefill data" (user copies manually).
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class JDText:
    url: str
    title: str = ""
    company: str = ""
    location: str = ""
    raw_text: str = ""
    keywords: List[str] = field(default_factory=list)
    source: str = ""  # adapter / site name

    def summary(self) -> str:
        head = f"{self.company or '(unknown company)'} — {self.title or '(untitled role)'}"
        if self.location:
            head += f"  [{self.location}]"
        return head


class SiteAdapter(abc.ABC):
    """One adapter per recruiting site."""
    name: str = "generic"
    # True if the site's ToS prohibit automated form interaction.
    tos_blocks_automation: bool = False

    @abc.abstractmethod
    def read_jd(self, url: str) -> JDText:
        ...

    def prefill_form(self, jd: JDText, profile: dict, page=None) -> bool:
        """Fill the application form. Does NOT submit. Returns False if unsupported."""
        return False

    def submit(self, jd: JDText, page=None) -> bool:
        """Submit the form. MUST block on confirm() first; never auto-submits.

        Returns True only if the user confirmed AND the submit succeeded.
        Returns False on user cancel, missing browser, or click failure.
        """
        raise NotImplementedError

    def capabilities(self) -> dict:
        return {
            "site": self.name,
            "read_jd": True,
            "prefill": not self.tos_blocks_automation,
            "submit": not self.tos_blocks_automation,
            "note": "ToS blocks automation; degrade to open-page + show-data"
                    if self.tos_blocks_automation else "",
        }
