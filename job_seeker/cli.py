"""python -m job_seeker — top-level orchestrator (Phase 4 + 5).

Subcommands:
  init          Scaffold LaTeX_Resume_<SCRIPT>/ (script-tagged variants) from
                resume_template, create docs/experience_bank.md, and smoke-compile
                the sample.
  tailor        JD + experience bank -> a tailored variant .tex (Phase 4 drafter).
  cover-letter  JD + experience bank -> a script-aware cover-letter DRAFT (Phase 4).
  i18n-audit    Static scan for leftover single-script / ASCII-only assumptions
                and old "CJK-first" framing (Phase 5 moat audit).
  init-variant  Scaffold a new LaTeX_Resume_<SCRIPT>/ + variant.json manifest.
  list-variants List discovered variant manifests (language-tagged).
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SAMPLE_TEX = ROOT / "resume_template" / "sample-resume-en_US-zh_CN.tex"


def _scaffold_one(target: Path, source: Path) -> bool:
    """Copy the template tree into ``target`` if it is empty/missing.

    Returns True if it actually scaffolded (False = already populated).
    """
    if target.exists() and any(target.iterdir()):
        return False
    target.mkdir(exist_ok=True)
    for p in source.iterdir():
        dst = target / p.name
        if p.is_file():
            shutil.copy2(p, dst)
        elif p.is_dir():
            shutil.copytree(p, dst, dirs_exist_ok=True)
    return True


def _baseline_variant_dirs() -> list:
    """Private resume dirs to scaffold on ``init``.

    Prefer any existing LaTeX_Resume_* dirs; otherwise scaffold the CN/EN
    baseline bilingual pair. This way adding LaTeX_Resume_RU/ (or _AR, _HE, …)
    to a private fork is picked up automatically — every writing system is a
    first-class citizen, not just CN/EN.
    """
    existing = sorted(
        (p for p in ROOT.glob("LaTeX_Resume_*") if p.is_dir()),
        key=lambda p: p.name,
    )
    if existing:
        return existing
    return [ROOT / "LaTeX_Resume_CN", ROOT / "LaTeX_Resume_EN"]


def _cmd_init(args) -> int:
    tmpl = ROOT / "resume_template"
    if not tmpl.exists():
        print("[init] ERROR: resume_template/ not found. Run from the repo root.")
        return 1

    print("[init] scaffolding private resume directories (gitignored)...")
    for d in _baseline_variant_dirs():
        name = d.name
        if _scaffold_one(d, tmpl):
            print(f"[init]   copied resume_template/* -> {name}/  (personalize the .tex, then `make build`)")
        else:
            print(f"[init]   {name}/ already populated — skipped.")

    eb = ROOT / "docs" / "experience_bank.md"
    ex = ROOT / "docs" / "experience_bank.example.md"
    if not eb.exists() and ex.exists():
        shutil.copy2(ex, eb)
        print("[init] created docs/experience_bank.md (private, gitignored).")

    print("[init] smoke-compiling the sample resume...")
    sample = tmpl / "sample-resume-en_US-zh_CN.tex"
    if sample.exists():
        rc = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", sample.name],
            cwd=str(tmpl), capture_output=True, text=True,
        ).returncode
        pdf = tmpl / "sample-resume-en_US-zh_CN.pdf"
        if rc == 0 and pdf.exists():
            print(f"[init] sample PDF built: {pdf.relative_to(ROOT)}")
        else:
            print("[init] NOTE: needs xelatex on PATH. Use GitHub Codespaces "
                  "(.devcontainer/) or install TeX Live — see docs/BUILD_MAC.md.")

    print()
    print("Next steps:")
    print("  1. Edit LaTeX_Resume_<SCRIPT>/*.tex (e.g. LaTeX_Resume_CN/) with your details.")
    print("  2. make build                    # compile all variants")
    print("  3. make fidelity                 # see the format-conversion matrix")
    print("  4. make apply-dryrun URL=<JD>    # JD -> variant recommendation")
    return 0


# --------------------------------------------------------------------------- #
# Phase 4 — tailor / cover-letter
# --------------------------------------------------------------------------- #

def _load_jd_text(args) -> tuple[str, str]:
    """Return (jd_text, jd_source) from --jd-file or --url. Offline-first."""
    if args.jd_file:
        p = Path(args.jd_file).expanduser()
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix.lower() in (".html", ".htm"):
            from bs4 import BeautifulSoup
            text = BeautifulSoup(text, "html.parser").get_text(separator="\n")
        return text.strip(), args.jd_file
    if args.url:
        from apply.adapters import pick_adapter
        jd = pick_adapter(args.url).read_jd(args.url)
        return (jd.raw_text or "").strip(), args.url
    return "", ""


def _experience_bank_text() -> str:
    """Read the private experience bank, falling back to the public example."""
    eb = ROOT / "docs" / "experience_bank.md"
    ex = ROOT / "docs" / "experience_bank.example.md"
    path = eb if eb.is_file() else ex
    if not path.is_file():
        return ""
    print(f"[tailor] experience bank: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def _resolve_base_tex(args) -> Path | None:
    """Resolve the base .tex for tailor (explicit --base, or --variant, or sample)."""
    if getattr(args, "base", None):
        p = Path(args.base).expanduser()
        if p.is_file():
            return p.resolve()
        print(f"[tailor] NOTE: --base {args.base} not found; falling back to sample.")
    if getattr(args, "variant", None):
        try:
            from apply.mapping.variant_renderer import find_variant_tex
            return find_variant_tex(args.variant)
        except FileNotFoundError:
            print(f"[tailor] NOTE: variant '{args.variant}' not found; "
                  "falling back to the sample template.")
    if SAMPLE_TEX.is_file():
        return SAMPLE_TEX
    print("[tailor] ERROR: no base .tex found (sample template missing).")
    return None


def _cmd_tailor(args) -> int:
    from job_seeker.tailor import run_tailor

    jd_text, jd_source = _load_jd_text(args)
    if not jd_text:
        print("[tailor] ERROR: provide --jd-file <path> (or --url).")
        return 2
    bank_text = _experience_bank_text()
    if not bank_text:
        print("[tailor] ERROR: no experience bank found (docs/experience_bank.md).")
        return 2
    base_tex = _resolve_base_tex(args)

    out_dir = Path(args.out) if args.out else ROOT / "outputs" / "tailored"
    res = run_tailor(jd_text, bank_text, base_tex=base_tex, out_dir=out_dir,
                     top_n=args.top_n, jd_source=jd_source)
    print(res.format_text())

    if args.honesty_check and res.new_tex:
        from apply.honesty_check import run_honesty_check
        written = next((n.split(": ", 1)[1] for n in res.notes
                        if n.startswith("wrote tailored .tex")), None)
        if written and Path(written).is_file():
            print("\n" + run_honesty_check(written).format_text())
    return 0


def _cmd_cover_letter(args) -> int:
    from job_seeker.cover_letter import run_cover_letter

    jd_text, jd_source = _load_jd_text(args)
    if not jd_text:
        print("[cover-letter] ERROR: provide --jd-file <path> (or --url).")
        return 2
    bank_text = _experience_bank_text()
    if not bank_text:
        print("[cover-letter] ERROR: no experience bank found (docs/experience_bank.md).")
        return 2
    name = args.name or os.environ.get("JOB_SEEKER_NAME", "")
    draft = run_cover_letter(jd_text, bank_text, name=name, jd_source=jd_source,
                             top_n=args.top_n)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(draft, encoding="utf-8")
        print(f"[cover-letter] wrote DRAFT: {out}")
    else:
        print(draft)
    return 0


# --------------------------------------------------------------------------- #
# Phase 5 — i18n-audit / init-variant / list-variants
# --------------------------------------------------------------------------- #

def _cmd_i18n_audit(args) -> int:
    # scripts/i18n_audit.py is the source of truth; import lazily so the rest
    # of the CLI works even if that script moves. Register in sys.modules
    # before exec so its dataclass decorators can resolve __module__.
    import importlib.util
    p = ROOT / "scripts" / "i18n_audit.py"
    spec = importlib.util.spec_from_file_location("i18n_audit", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["i18n_audit"] = mod
    spec.loader.exec_module(mod)
    return mod.main(["--strict"] if args.strict else [])


def _cmd_init_variant(args) -> int:
    from job_seeker.variants import init_variant, manifest_path
    try:
        target = init_variant(args.script, language=args.language)
    except FileNotFoundError as e:
        print(f"[init-variant] ERROR: {e}")
        return 1
    print(f"[init-variant] scaffolded {target.relative_to(ROOT)}/ from resume_template/")
    print(f"[init-variant] wrote manifest: {manifest_path(target).relative_to(ROOT)}")
    print(f"[init-variant] next: personalize the .tex in {target.name}/, then `make build`.")
    return 0


def _cmd_list_variants(args) -> int:
    from job_seeker.variants import read_manifests
    manifests = read_manifests()
    if not manifests:
        print("[list-variants] no variant.json manifests found.")
        print("  (LaTeX_Resume_*/ dirs are still discovered by glob; "
              "run `python -m job_seeker init-variant --script RU` to add one.)")
        return 0
    print(f"[list-variants] {len(manifests)} variant manifest(s):")
    for m in manifests:
        print(f"  - {m['_dir']:22} script={m.get('script','?'):10} "
              f"language={m.get('language','?'):6} base={m.get('base_template','?')}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m job_seeker",
        description="job-seeker orchestrator (init / tailor / cover-letter / "
                    "i18n-audit / init-variant).",
    )
    sub = ap.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="scaffold private resume dirs + experience bank + smoke compile")
    p_init.set_defaults(func=_cmd_init)

    # ---- tailor (Phase 4) ----
    p_tailor = sub.add_parser("tailor",
                              help="JD + experience bank -> tailored variant .tex (drafter pass)")
    g = p_tailor.add_mutually_exclusive_group(required=True)
    g.add_argument("--jd-file", help="local JD file (html/md/txt)")
    g.add_argument("--url", help="JD URL (offline-first: prefer --jd-file)")
    p_tailor.add_argument("--variant", help="base variant name (default: sample template)")
    p_tailor.add_argument("--base", help="explicit base .tex path")
    p_tailor.add_argument("--out", help="output dir (default: outputs/tailored/)")
    p_tailor.add_argument("--top-n", type=int, default=8, help="max bullets to select")
    p_tailor.add_argument("--honesty-check", action="store_true",
                          help="also run the heuristic honesty check on the tailored .tex")
    p_tailor.set_defaults(func=_cmd_tailor)

    # ---- cover-letter (Phase 4) ----
    p_cl = sub.add_parser("cover-letter",
                          help="JD + experience bank -> script-aware cover-letter DRAFT")
    g = p_cl.add_mutually_exclusive_group(required=True)
    g.add_argument("--jd-file", help="local JD file (html/md/txt)")
    g.add_argument("--url", help="JD URL")
    p_cl.add_argument("--out", help="output .md file (default: stdout)")
    p_cl.add_argument("--name", help="your name (default: $JOB_SEEKER_NAME)")
    p_cl.add_argument("--top-n", type=int, default=5, help="max bullets to cite")
    p_cl.set_defaults(func=_cmd_cover_letter)

    # ---- i18n-audit (Phase 5) ----
    p_aud = sub.add_parser("i18n-audit",
                           help="scan for leftover single-script / ASCII-only assumptions")
    p_aud.add_argument("--strict", action="store_true",
                       help="exit 1 if any ERROR-level finding is reported")
    p_aud.set_defaults(func=_cmd_i18n_audit)

    # ---- init-variant (Phase 5) ----
    p_iv = sub.add_parser("init-variant",
                          help="scaffold a new LaTeX_Resume_<SCRIPT>/ + variant.json")
    p_iv.add_argument("--script", required=True, help="script suffix, e.g. RU, AR, HE, JA")
    p_iv.add_argument("--language", help="language code, e.g. ru, ar, he, ja (default: suffix lowercased)")
    p_iv.set_defaults(func=_cmd_init_variant)

    # ---- list-variants (Phase 5) ----
    p_lv = sub.add_parser("list-variants", help="list discovered variant manifests")
    p_lv.set_defaults(func=_cmd_list_variants)

    # Reserved for later (docs/ROADMAP) — declared so the help surfaces the roadmap.
    for name, help_ in (("ats-check", "(planned) ATS readability check on a PDF "
                                      "(use `python -m apply --ats-check` meanwhile)"),
                        ("templates", "(planned) list/add resume templates")):
        sub.add_parser(name, help=help_).set_defaults(func=None)

    args = ap.parse_args(argv)
    if not getattr(args, "cmd", None):
        ap.print_help()
        return 0
    if args.func is None:
        print(f"[job_seeker] '{args.cmd}' is planned but not yet implemented "
              f"(see docs/ROADMAP_v0.4.md).")
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
