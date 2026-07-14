"""Human-in-the-loop confirmation gate.

This is the safety-critical component of Phase 3 (§3.1). `submit()` MUST call
`confirm()` and block on its return value before doing anything destructive.

Never auto-approves. To avoid hanging in CI / non-interactive shells:
  - env JOB_SEEKER_CONFIRM=yes  -> auto-approve (for scripted tests only)
  - env JOB_SEEKER_CONFIRM=no   -> auto-deny
  - non-tty stdin               -> deny (safe default)
"""
from __future__ import annotations

import os
import sys
from typing import Optional


def confirm(jd=None, prompt: str = "Submit this application? [y/N] ", default: bool = False) -> bool:
    """Block for a yes/no answer. Returns True only on explicit yes.

    `jd` is accepted for context (may be printed) but not required.
    """
    env = os.environ.get("JOB_SEEKER_CONFIRM", "").strip().lower()
    if env in ("yes", "y", "1", "true"):
        print("[confirm] auto-approved via JOB_SEEKER_CONFIRM=yes (scripted)")
        return True
    if env in ("no", "n", "0", "false"):
        print("[confirm] auto-denied via JOB_SEEKER_CONFIRM=no (scripted)")
        return False

    if not sys.stdin or not sys.stdin.isatty():
        print("[confirm] non-interactive stdin -> defaulting to NO (will not submit)")
        return False

    try:
        ans = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return ans in ("y", "yes")
