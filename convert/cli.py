"""CLI: python -m convert --input foo.md --output foo.pdf

Auto-routes a chain of adapters based on file extensions. Prints the chosen
route, warns about lossy steps, and exits non-zero on failure.
"""
from __future__ import annotations

import argparse
import sys

from .pipeline import Pipeline, route, _EDGES


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m convert",
        description="job-seeker format converter (MD / DOCX / PDF / LaTeX).",
    )
    ap.add_argument("--input", "-i", help="input file path")
    ap.add_argument("--output", "-o", help="output file path")
    ap.add_argument("--list-routes", action="store_true",
                    help="print supported conversion edges and exit")
    args = ap.parse_args(argv)

    if args.list_routes:
        for (a, b), cls in sorted(_EDGES.items()):
            note = f"  [LOSSY: {cls.lossy_note}]" if cls.lossy_note else ""
            print(f"  .{a} -> .{b}  ({cls.__name__}){note}")
        return 0

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
