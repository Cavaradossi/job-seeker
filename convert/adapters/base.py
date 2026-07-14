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

    @abc.abstractmethod
    def convert(self, input_path: str, output_path: str) -> bool:
        """Return True on success, False on failure."""
        ...

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
