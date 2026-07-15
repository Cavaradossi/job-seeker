"""python -m job_seeker — top-level entry point.

Subcommands:
  init   Scaffold LaTeX_Resume_CN/ + LaTeX_Resume_EN/ from resume_template,
         create docs/experience_bank.md, and smoke-compile the sample.

Future (see docs/ROADMAP_v0.4.md): tailor, ats-check, templates.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _scaffold_one(target: Path, source: Path) -> bool:
    """Copy the template tree into `target` if it is empty/missing.

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


def _cmd_init(args) -> int:
    tmpl = ROOT / "resume_template"
    if not tmpl.exists():
        print("[init] ERROR: resume_template/ not found. Run from the repo root.")
        return 1

    print("[init] scaffolding private resume directories (gitignored)...")
    for name in ("LaTeX_Resume_CN", "LaTeX_Resume_EN"):
        d = ROOT / name
        if _scaffold_one(d, tmpl):
            print(f"[init]   copied resume_template/* -> {name}/  (personalize the .tex, then `make build`)")
        else:
            print(f"[init]   {name}/ already populated — skipped.")

    # Private experience bank from the example.
    eb = ROOT / "docs" / "experience_bank.md"
    ex = ROOT / "docs" / "experience_bank.example.md"
    if not eb.exists() and ex.exists():
        shutil.copy2(ex, eb)
        print("[init] created docs/experience_bank.md (private, gitignored).")

    # Smoke-compile the sample so the user sees a PDF immediately.
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
    print("  1. Edit LaTeX_Resume_CN/*.tex (or LaTeX_Resume_EN/) with your details.")
    print("  2. make build                    # compile all variants")
    print("  3. make fidelity                 # see the format-conversion matrix")
    print("  4. make apply-dryrun URL=<JD>    # JD -> variant recommendation")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m job_seeker",
        description="job-seeker orchestrator (init / tailor / ats-check).",
    )
    sub = ap.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="scaffold private resume dirs + experience bank + smoke compile")
    p_init.set_defaults(func=_cmd_init)

    # Reserved for later phases (docs/ROADMAP_v0.4.md) — declared so the help
    # surfaces the roadmap, but they exit 2 until implemented.
    for name, help_ in (("tailor", "(planned) any-format resume + JD -> tailored PDF"),
                        ("ats-check", "(planned) ATS readability check on a PDF"),
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
