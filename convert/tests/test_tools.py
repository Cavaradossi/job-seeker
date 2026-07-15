"""Tests for convert.tools (cross-platform PATH / resolve)."""
from __future__ import annotations

import os
import sys

from convert.tools import _is_windows, _pathsep, env_with_tex, resolve


def test_pathsep_matches_os():
    assert _pathsep() == os.pathsep


def test_env_with_tex_uses_platform_pathsep():
    env = env_with_tex({"PATH": "C:\\existing" if _is_windows() else "/usr/bin"})
    parts = env["PATH"].split(_pathsep())
    assert len(parts) >= 1
    if _is_windows():
        assert any("existing" in p for p in parts)
    else:
        assert "/usr/bin" in parts


def test_resolve_xelatex_or_none():
    # Smoke: returns str or None, never raises
    p = resolve("xelatex")
    assert p is None or os.path.isfile(p)


def test_windows_prefers_xelatex_engine_order():
    from convert.adapters.latex_to_pdf import _pick_engine

    eng = _pick_engine()
    if eng is None:
        return
    if sys.platform == "win32":
        assert "xelatex" in eng.lower() or "latexmk" in eng.lower()
