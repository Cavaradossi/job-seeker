"""LaTeX -> PDF via xelatex (preferred) or latexmk.

Runs in the .tex's directory so local .cls / .sty and bundled fonts are
found (matches the repo's build_resumes.sh convention). This supports the
custom `resume` document class shipped in resume_template/.

Prefer latexmk when available (it handles multiple passes + biber). Fall
back to running xelatex twice to settle references/hyperref.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from .base import Adapter
from ..tools import resolve, env_with_tex


class LatexToPdf(Adapter):
    input_format = "tex"
    output_format = "pdf"

    def convert(self, input_path: str, output_path: str) -> bool:
        input_path = str(Path(input_path).expanduser().resolve())
        output_path = str(Path(output_path).expanduser().resolve())
        tex_dir = str(Path(input_path).parent)
        tex_name = Path(input_path).name
        base = Path(input_path).stem

        engine = resolve("latexmk") or resolve("xelatex")
        if not engine:
            print("[LatexToPdf] xelatex not found. See doc/BUILD_MAC.md.")
            return False

        self._ensure_parent(output_path)
        env = env_with_tex()
        is_latexmk = Path(engine).name.startswith("latexmk")

        if is_latexmk:
            cmd = [engine, "-xelatex", "-interaction=nonstopmode",
                   "-halt-on-error", tex_name]
        else:
            cmd = [engine, "-interaction=nonstopmode", "-halt-on-error", tex_name]

        ok, out = self._run(cmd, cwd=tex_dir, env=env)
        if not ok:
            self._dump(tex_dir, base, out)
            return False
        # plain xelatex: second pass to settle refs/hyperref (ignore benign failures)
        if not is_latexmk:
            self._run(cmd, cwd=tex_dir, env=env)

        produced = Path(tex_dir) / f"{base}.pdf"
        if not produced.exists():
            self._dump(tex_dir, base, out)
            return False
        shutil.copyfile(produced, output_path)
        self._cleanup(tex_dir, base)
        return True

    @staticmethod
    def _cleanup(tex_dir: str, base: str) -> None:
        for ext in ("aux", "log", "out", "fls", "fdb_latexmk", "toc", "synctex.gz", "xdv"):
            p = Path(tex_dir) / f"{base}.{ext}"
            if p.exists():
                try:
                    p.unlink()
                except OSError:
                    pass

    @staticmethod
    def _dump(tex_dir: str, base: str, out: str) -> None:
        log = Path(tex_dir) / f"{base}.log"
        print("[LatexToPdf] compilation failed.")
        if log.exists():
            try:
                tail = log.read_text(errors="replace").splitlines()[-40:]
                print("----- last 40 log lines -----")
                print("\n".join(tail))
                print("-----------------------------")
            except OSError:
                pass
        if out:
            print(out[-1500:])
