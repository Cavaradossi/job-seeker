"""Adapter ABC: convert(input_path, output_path) -> bool.

Each adapter performs a single format conversion. Adapters are subprocess-
based (pandoc / xelatex) and return True/False rather than raising on
expected failures (missing tool, compilation error). Programmer errors
(bad arguments) may still raise.
"""
from __future__ import annotations

import abc
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class Adapter(abc.ABC):
    """Base class for a single-step format converter.

    Subclasses declare `input_format` / `output_format` (extensions without
    the leading dot: "md", "tex", "pdf", "docx") and implement
    `convert(input_path, output_path) -> bool`.
    """

    input_format: str = ""
    output_format: str = ""
    # Human-readable lossiness note. None = intended to be lossless.
    lossy_note: Optional[str] = None
    # Fidelity tier override. None => inferred from lossy_note
    # (None -> "lossless", otherwise "lossy"). Set explicitly to "text-only"
    # for extractors (e.g. PDF -> Markdown via text-layer extraction).
    fidelity: Optional[str] = None

    @abc.abstractmethod
    def convert(self, input_path: str, output_path: str) -> bool:
        """Return True on success, False on failure."""
        ...

    # ---- fidelity reporting (see `convert --fidelity-matrix`) ----

    _TIER_RANK = {"lossless": 0, "lossy": 1, "text-only": 2}

    @classmethod
    def fidelity_tier(cls) -> str:
        """Return the fidelity tier: "lossless" | "lossy" | "text-only"."""
        if cls.fidelity:
            return cls.fidelity
        return "lossless" if cls.lossy_note is None else "lossy"

    @classmethod
    def fidelity_report(cls) -> str:
        """One-line fidelity summary, e.g. 'lossy: custom macros do not survive'."""
        tier = cls.fidelity_tier()
        note = cls.lossy_note or ""
        return f"{tier}" + (f": {note}" if note else "")

    @classmethod
    def worse_tier(cls, *tiers: str) -> str:
        """Return the worst (most lossy) tier among the given tiers."""
        if not tiers:
            return "lossless"
        return max(tiers, key=lambda t: cls._TIER_RANK.get(t, 1))

    # ---- shared subprocess / filesystem helpers ----

    @staticmethod
    def _run(cmd, cwd=None, env=None, timeout: int = 240) -> tuple[bool, str]:
        """Run a command; return (ok, combined stdout+stderr)."""
        try:
            p = subprocess.run(
                cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout,
            )
            return p.returncode == 0, (p.stdout or "") + (p.stderr or "")
        except FileNotFoundError:
            return False, f"command not found: {cmd[0]}"
        except subprocess.TimeoutExpired:
            return False, f"timeout after {timeout}s running: {' '.join(cmd[:3])} ..."

    @staticmethod
    def _ensure_parent(output_path: str) -> None:
        Path(output_path).expanduser().parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def name(cls) -> str:
        return f"{cls.input_format}->{cls.output_format}"
