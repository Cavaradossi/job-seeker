"""Generic ATS / public job-page adapter.

Covers Workday, Greenhouse, Lever, and any plain-HTML job posting.

read_jd    : HTTP fetch + BeautifulSoup text extraction (no login, no browser).
prefill    : Playwright (lazy import), best-effort field fill by label/name.
submit     : blocks on confirm() (§3.1); clicks submit only after explicit yes.

Degrades gracefully when Playwright is absent or ToS blocks automation.
"""
from __future__ import annotations

from typing import Tuple

from .base import SiteAdapter, JDText


class GenericAdapter(SiteAdapter):
    name = "generic"
    tos_blocks_automation = False

    # Default Accept-Language header. We do NOT assume English-only: advertise a
    # broad set of language/region tags so localized job boards (CN/ZH, TW/ZH,
    # JP/JA, KR/KO, RU, AR, HE, FR, DE) return HTML in the candidate's language
    # instead of a forced-English page or a 406. Override per-adapter when a
    # board needs a specific tag. Every writing system is a first-class citizen.
    DEFAULT_ACCEPT_LANGUAGE = (
        "en, zh-CN, zh-TW, ja, ko, ru, ar, he, fr, de;q=0.8"
    )

    # ------------------------------------------------------------------ read_jd
    def read_jd(self, url: str) -> JDText:
        text, title, company, location = self._fetch_and_parse(url)
        return JDText(url=url, title=title, company=company, location=location,
                      raw_text=text, source=self.name)

    def _fetch_and_parse(self, url: str) -> Tuple[str, str, str, str]:
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError as e:
            return f"[deps missing: {e}]", "", "", ""

        headers = {
            "User-Agent": ("Mozilla/5.0 (job-seeker apply/0.1; "
                           "+https://github.com/your-org/job-seeker)"),
            "Accept-Language": self.DEFAULT_ACCEPT_LANGUAGE,
        }
        try:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
        except Exception as e:
            return f"[fetch failed: {e}]", "", "", ""

        soup = BeautifulSoup(r.text, "html.parser")
        title = (self._meta(soup, "og:title")
                 or (soup.title.string.strip() if soup.title and soup.title.string else ""))
        company = self._meta(soup, "og:site_name") or ""
        location = self._extract_location(soup)
        text = self._extract_text(soup)
        return text, title, company, location

    @staticmethod
    def _meta(soup, prop: str) -> str:
        m = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        return m.get("content", "").strip() if m and m.get("content") else ""

    @staticmethod
    def _extract_location(soup) -> str:
        for prop in ("jobLocation", "addressLocality", "addressRegion"):
            el = soup.find(attrs={"itemprop": prop})
            if el:
                return el.get_text(strip=True)
        return ""

    @staticmethod
    def _extract_text(soup) -> str:
        for tag in soup(["script", "style", "noscript", "svg", "header",
                         "footer", "nav", "aside", "form"]):
            tag.decompose()
        main = soup.find("main") or soup.find("article") or soup.body or soup
        lines = [ln.strip() for ln in main.get_text(separator="\n").splitlines() if ln.strip()]
        # collapse short repeats
        return "\n".join(lines)

    # ------------------------------------------------------------------ prefill
    def prefill_form(self, jd: JDText, profile: dict, page=None) -> bool:
        if page is None:
            return False
        return self._prefill(page, profile)

    def _prefill(self, page, profile: dict) -> bool:
        # `name` (the full name) is the canonical identifier and is attempted
        # first. `first_name`/`last_name` are OPTIONAL secondary fills, used only
        # when a form structurally requires separate given/family fields. We do
        # NOT enforce Latin-style name splitting — many writing systems (CJK,
        # Arabic, Hebrew, Cyrillic, …) have no clean given/family split, so the
        # single full `name` is the source of truth and first/last are derived.
        fields = [
            ("email", profile.get("email", "")),
            ("phone", profile.get("phone", "")),
            ("mobile", profile.get("phone", "")),
            ("full name", profile.get("name", "")),
            ("name", profile.get("name", "")),
            ("first name", profile.get("first_name", "")),
            ("last name", profile.get("last_name", "")),
        ]
        filled = 0
        for label, value in fields:
            if not value:
                continue
            selectors = [
                f"label:has-text('{label}')",
                f"input[placeholder*='{label}' i]",
                f"input[name*='{label.split()[0]}' i]",
                f"input[type=email]" if "email" in label else None,
                f"input[type=tel]" if "phone" in label or "mobile" in label else None,
            ]
            for sel in selectors:
                if not sel:
                    continue
                try:
                    loc = page.locator(sel).first
                    if loc.count() > 0:
                        loc.fill(value)
                        filled += 1
                        break
                except Exception:
                    continue
        return filled > 0

    # ------------------------------------------------------------------ submit
    def submit(self, jd: JDText, page=None) -> bool:
        from ..confirm import confirm
        approved = confirm(
            jd,
            prompt=f"[{self.name}] Submit application to "
                   f"{jd.company or jd.url}? [y/N] ",
        )
        if not approved:
            return False  # user cancelled — NOT submitted
        if page is None:
            print("[submit] no browser session (rehearsal mode) — nothing actually submitted.")
            return False
        for sel in ("button[type=submit]", "input[type=submit]",
                    "button:has-text('Submit')", "button:has-text('Apply')"):
            try:
                loc = page.locator(sel).first
                if loc.count() > 0:
                    loc.click()
                    return True
            except Exception:
                continue
        print("[submit] no submit button found.")
        return False
