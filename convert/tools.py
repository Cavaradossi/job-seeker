"""Locate external tools (pandoc, xelatex, latexmk) across platforms.

Non-interactive shells often don't source the user's shell rc, so TeX Live
and ~/.local/bin may be absent from PATH even when installed. We check PATH
first, then fall back to common install locations (MacTeX, user-level TeX
Live, Homebrew, ~/.local/bin, the project venv). When invoking TeX binaries
we also prepend their bin dir to PATH so xelatex/latexmk find support tools
(kpsewhich, mktexmf, ...).
"""
from __future__ import annotations

import glob
import os
import shutil
from pathlib import Path
from typing import List, Optional


def _tex_bin_dirs() -> List[str]:
    """Candidate TeX bin directories, newest-year first."""
    dirs: List[str] = ["/Library/TeX/texbin", "/usr/bin"]
    for pat in (
        str(Path.home() / "texlive/*/bin/*"),
        "/usr/local/texlive/*/bin/*",
    ):
        dirs.extend(sorted(glob.glob(pat), reverse=True))
    return dirs


def _extra_bin_dirs() -> List[str]:
    """Non-TeX tool locations (pandoc, etc.)."""
    repo = Path(__file__).resolve().parent.parent
    return [
        str(Path.home() / ".local/bin"),
        "/opt/homebrew/bin",
        "/usr/local/bin",
        str(repo / ".venv/bin"),
    ]


def _all_search_dirs() -> List[str]:
    seen, out = set(), []
    for d in _tex_bin_dirs() + _extra_bin_dirs():
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def resolve(name: str) -> Optional[str]:
    """Absolute path to `name` if found on PATH or known locations, else None."""
    found = shutil.which(name)
    if found:
        return found
    for d in _all_search_dirs():
        p = Path(d) / name
        if p.exists() and os.access(p, os.X_OK):
            return str(p)
    return None


def env_with_tex(env: Optional[dict] = None) -> dict:
    """Copy of env with TeX + extra bin dirs prepended to PATH (for subprocess)."""
    e = dict(env or os.environ)
    extra = [d for d in _all_search_dirs() if Path(d).is_dir()]
    existing = e.get("PATH", "")
    existing_parts = existing.split(":")
    prepend = [d for d in extra if d not in existing_parts]
    e["PATH"] = ":".join(prepend + ([existing] if existing else []))
    return e
