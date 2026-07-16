"""CLI: python -m apply --url <jd> [--variant X] [--dry-run] [--rehearse]

Flow:
  1. read_jd            (HTTP fetch or local --jd-file)  — always works
  2. recommend_variant  (rule-based) + render_variant (compile .tex -> PDF)
  3. branch:
       --dry-run  : print JD + variant + PDF, audit 'dry_run'. No browser.
       --rehearse : exercise the confirm() gate WITHOUT a browser
                    (demonstrates the §3.1 human-in-the-loop pause). audit outcome.
       default    : live flow. If Playwright is installed and ToS allow it,
                    prefill the form then call submit() (which BLOCKS on
                    confirm()). Otherwise degrade to open-page + show-data.

Credentials come from env vars (JOB_SEEKER_NAME / EMAIL / PHONE) or a
--profile JSON file — never from the repo.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import webbrowser
from pathlib import Path

from .adapters import pick_adapter
from .adapters.base import JDText
from .mapping.jd_to_variant import recommend_variant
from .mapping.variant_renderer import render_variant
from .audit import log_event
from convert.ats_check import run_ats_check
from .honesty_check import run_honesty_check


def load_profile(args) -> dict:
    profile = {
        "name": os.environ.get("JOB_SEEKER_NAME", ""),
        "first_name": os.environ.get("JOB_SEEKER_FIRST_NAME", ""),
        "last_name": os.environ.get("JOB_SEEKER_LAST_NAME", ""),
        "email": os.environ.get("JOB_SEEKER_EMAIL", ""),
        "phone": os.environ.get("JOB_SEEKER_PHONE", ""),
    }
    if args.profile:
        try:
            profile.update(json.loads(Path(args.profile).read_text(encoding="utf-8")))
        except Exception as e:
            print(f"[apply] WARNING: could not load --profile {args.profile}: {e}")
    return profile


def read_jd(adapter, args) -> JDText:
    if args.jd_file:
        p = Path(args.jd_file).expanduser()
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix.lower() in (".html", ".htm"):
            from bs4 import BeautifulSoup
            text = BeautifulSoup(text, "html.parser").get_text(separator="\n")
        return JDText(url=args.jd_file, title=p.stem, company="", location="",
                      raw_text=text.strip(), source="local-file")
    return adapter.read_jd(args.url)


def print_jd(jd: JDText) -> None:
    print(f"[apply] JD: {jd.summary()}")
    print(f"[apply] source: {jd.source} | url: {jd.url}")
    snippet = (jd.raw_text or "").strip().replace("\n", " ")
    print(f"[apply] text ({len(snippet)} chars): "
          f"{snippet[:300]}{'...' if len(snippet) > 300 else ''}")


def _open_and_show(url: str, profile: dict, pdf) -> None:
    print("[apply] prefill data (copy manually into the form):")
    for k, v in profile.items():
        if v:
            print(f"   {k}: {v}")
    if pdf:
        print(f"   resume PDF: {pdf}")
    if url:
        try:
            webbrowser.open(url)
            print(f"[apply] opened {url} in your default browser.")
        except Exception:
            pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m apply",
        description="job-seeker browser-assisted application (human-in-the-loop).",
    )
    g = ap.add_mutually_exclusive_group(required=False)
    g.add_argument("--url", help="JD URL to read")
    g.add_argument("--jd-file", help="local JD file (html/md/txt) — offline alternative to --url")
    ap.add_argument("--variant", help="resume variant name/path (default: auto-recommend)")
    ap.add_argument("--dry-run", action="store_true",
                    help="fetch JD + recommend variant + render PDF; no browser, no submit")
    ap.add_argument("--rehearse", action="store_true",
                    help="run the confirm() gate without a browser (tests the pause)")
    ap.add_argument("--profile", help="profile JSON file (else env vars JOB_SEEKER_NAME/EMAIL/PHONE)")
    ap.add_argument("--ats-check", action="store_true",
                    help="run the ATS readability check on the rendered PDF "
                         "(uses the JD for keyword coverage). Advisory, non-blocking.")
    ap.add_argument("--honesty-check", metavar="TEX",
                    help="run the heuristic honesty check on a resume .tex "
                         "(advisory; flags vague/absolute/scope-inflated claims).")
    args = ap.parse_args(argv)

    # ---- standalone honesty check (does not need a JD or browser) ----
    if args.honesty_check:
        rep = run_honesty_check(args.honesty_check)
        print(rep.format_text())
        return 0

    if not (args.url or args.jd_file):
        ap.error("one of --url / --jd-file is required (or use --honesty-check <tex>)")

    adapter = pick_adapter(args.url or "")
    jd = read_jd(adapter, args)
    print_jd(jd)

    rec = recommend_variant(jd)
    variant = args.variant or rec.variant
    if rec.matched_keywords:
        print(f"[apply] recommended variant: {rec.variant}  ({rec.reason}) "
              f"[matched: {', '.join(rec.matched_keywords)}]")
    else:
        print(f"[apply] recommended variant: {rec.variant}  ({rec.reason})")
    if args.variant and args.variant != rec.variant:
        variant = args.variant
        print(f"[apply] using --variant override: {variant}")

    pdf = None
    try:
        pdf = render_variant(variant)
        print(f"[apply] rendered PDF: {pdf}")
    except FileNotFoundError as e:
        print(f"[apply] NOTE: {e}")
        print("[apply] (Public template repo ships only the sample variant. "
              "Add your variants to LaTeX_Resume_CN/ or LaTeX_Resume_EN/.)")
    except RuntimeError as e:
        print(f"[apply] NOTE: {e}")

    # ---- optional ATS readability check on the rendered PDF ----
    if args.ats_check and pdf:
        rep = run_ats_check(str(pdf), jd_text=jd.raw_text)
        print(rep.format_text())

    # ---- dry run: stop here, audit, exit 0 ----
    if args.dry_run:
        print("[apply] DRY RUN — no browser, no submit.")
        log_event(jd, variant, str(pdf) if pdf else "", "dry_run", adapter.name,
                  notes="dry-run")
        return 0

    profile = load_profile(args)
    caps = adapter.capabilities()
    print(f"[apply] adapter: {adapter.name} | prefill={caps['prefill']} | "
          f"submit={caps['submit']} {caps['note']}")

    # ---- rehearse: exercise the confirm gate with no browser ----
    if args.rehearse:
        print("[apply] REHEARSE — no browser; exercising the confirmation gate only "
              "(no real submission).")
        from .confirm import confirm
        approved = confirm(
            jd,
            prompt=f"[{adapter.name}] (rehearse) Submit application to "
                   f"{jd.company or jd.url}? [y/N] ",
        )
        status = "rehearse_confirmed" if approved else "rehearse_cancelled"
        log_event(jd, variant, str(pdf) if pdf else "", status, adapter.name,
                  notes="rehearse")
        print(f"[apply] outcome: {status}")
        return 0

    # ---- live flow ----
    if adapter.tos_blocks_automation:
        print(f"[apply] ToS for {adapter.name} blocks automation — "
              "degrading to open-page + show-data.")
        _open_and_show(args.url or "", profile, pdf)
        log_event(jd, variant, str(pdf) if pdf else "", "degraded", adapter.name,
                  notes="tos-blocks; manual")
        return 0

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[apply] Playwright not installed — degrading to open-page + show-data.")
        print("[apply] Install for live prefill:  "
              "pip install 'playwright>=1.40' && playwright install chromium")
        _open_and_show(args.url or "", profile, pdf)
        log_event(jd, variant, str(pdf) if pdf else "", "degraded", adapter.name,
                  notes="no-playwright; manual")
        return 0

    print("[apply] launching browser (headless=False)…")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto(args.url, wait_until="domcontentloaded")
            filled = adapter.prefill_form(jd, profile, page)
            print(f"[apply] prefill: {'fields filled' if filled else 'no fields matched'}")
            if pdf:
                try:
                    page.locator("input[type=file]").first.set_input_files(str(pdf))
                    print("[apply] resume PDF attached to upload field.")
                except Exception:
                    print("[apply] no file-upload field found (attach PDF manually).")
            # IRON RULE: submit() blocks on confirm() — never auto-submits.
            submitted = adapter.submit(jd, page=page)
        finally:
            browser.close()

    status = "submitted" if submitted else "user_cancelled"
    log_event(jd, variant, str(pdf) if pdf else "", status, adapter.name)
    print(f"[apply] outcome: {status}")
    return 0
