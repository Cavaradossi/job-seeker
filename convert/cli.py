"""CLI: python -m convert --input foo.md --output foo.pdf

Auto-routes a chain of adapters based on file extensions. Prints the chosen
route, warns about lossy steps, and exits non-zero on failure.
"""
from __future__ import annotations

import argparse
import sys

from .pipeline import Pipeline, route, _EDGES
from .adapters.base import Adapter


def _print_fidelity_matrix() -> int:
    """Print the 4x4 fidelity matrix. Routed pairs show the worst tier on path."""
    exts = ["md", "tex", "docx", "pdf"]
    glyph = {"lossless": "OK", "lossy": "~", "text-only": "T"}
    print("Fidelity matrix  (rows = from, cols = to)")
    print("  Legend: OK = lossless · ~ = lossy · T = text-only · - = same format")
    print("          (routed pairs show the worst tier along the BFS path)")
    print()
    print(f"  {'from\\\\to':>9}  " + "  ".join(f"{e:>5}" for e in exts))
    for a in exts:
        cells = []
        for b in exts:
            if a == b:
                cells.append("  -  ")
                continue
            try:
                adapters = route(f"x.{a}", f"y.{b}")
            except ValueError:
                cells.append(" n/a ")
                continue
            if not adapters:
                cells.append(" OK  ")
                continue
            worst = Adapter.worse_tier(*(cls.fidelity_tier() for cls in adapters))
            cells.append(f"  {glyph.get(worst, '?')}  ")
        print(f"  {a:>9}  " + "  ".join(cells))
    print()
    print("Per-edge detail:  python -m convert --list-routes")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m convert",
        description="job-seeker format converter (MD / DOCX / PDF / LaTeX).",
    )
    ap.add_argument("--input", "-i", help="input file path")
    ap.add_argument("--output", "-o", help="output file path")
    ap.add_argument("--list-routes", action="store_true",
                    help="print supported conversion edges and exit")
    ap.add_argument("--fidelity-matrix", action="store_true",
                    help="print the 4x4 fidelity matrix (lossless/lossy/text-only) and exit")
    args = ap.parse_args(argv)

    if args.list_routes:
        for (a, b), cls in sorted(_EDGES.items()):
            note = f"  [{cls.fidelity_tier().upper()}] {cls.lossy_note}" if cls.lossy_note else ""
            print(f"  .{a} -> .{b}  ({cls.__name__}){note}")
        return 0

    if args.fidelity_matrix:
        return _print_fidelity_matrix()

    if not args.input or not args.output:
        ap.error("the following arguments are required: --input/-i, --output/-o "
                 "(unless --list-routes)")

    try:
        adapters = route(args.input, args.output)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    if not adapters:
        print(f"[convert] same type; copying {args.input} -> {args.output}")
        ok = Pipeline.auto(args.input, args.output)
    else:
        chain = " -> ".join(f".{a.input_format}" for a in adapters) + f" -> .{adapters[-1].output_format}"
        print(f"[convert] route: {chain}")
        for a in adapters:
            if a.lossy_note:
                print(f"[convert]   WARNING ({a.name()}): {a.lossy_note}")
        ok = Pipeline(*adapters).run(args.input, args.output)

    if ok:
        print(f"[convert] OK -> {args.output}")
        return 0
    print(f"[convert] FAILED -> {args.output}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
