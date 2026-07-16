"""Tests for scripts/i18n_audit.py (Phase 5 — i18n moat audit)."""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_audit():
    """Load scripts/i18n_audit.py as an importable module (it is not a package)."""
    p = ROOT / "scripts" / "i18n_audit.py"
    spec = importlib.util.spec_from_file_location("i18n_audit_test_mod", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["i18n_audit_test_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_root() -> Path:
    root = Path(tempfile.mkdtemp())
    (root / "apply").mkdir()
    (root / "convert").mkdir()
    (root / "job_seeker").mkdir()
    (root / "docs" / "skill").mkdir(parents=True)
    return root


def test_audit_flags_hardcoded_pair():
    audit = _load_audit()
    root = _make_root()
    try:
        (root / "apply" / "bad.py").write_text(
            'VARIANTS = ["LaTeX_Resume_CN", "LaTeX_Resume_EN"]\n', encoding="utf-8")
        rep = audit.run_audit(root)
        codes = [(f.level, f.code) for f in rep.findings]
        assert ("ERROR", "HARDCODED_PAIR") in codes
    finally:
        shutil.rmtree(root)


def test_audit_flags_ascii_only_tokenizer():
    audit = _load_audit()
    root = _make_root()
    try:
        (root / "convert" / "bad_tok.py").write_text(
            'import re\n'
            'tokens = re.findall(r"[A-Za-z][A-Za-z\\-]{2,}", text)\n',
            encoding="utf-8")
        rep = audit.run_audit(root)
        codes = [(f.level, f.code) for f in rep.findings]
        assert ("WARN", "ASCII_TOKEN") in codes
    finally:
        shutil.rmtree(root)


def test_audit_flags_old_framing_in_docs():
    audit = _load_audit()
    root = _make_root()
    try:
        (root / "docs" / "skill" / "SKILL.md").write_text(
            "Our moat is CJK-first bilingual i18n.\n", encoding="utf-8")
        rep = audit.run_audit(root)
        codes = [(f.level, f.code) for f in rep.findings]
        assert ("ERROR", "OLD_FRAMING") in codes
    finally:
        shutil.rmtree(root)


def test_audit_clean_repo_reports_zero_errors():
    # The real repo should pass the moat audit with zero ERRORs.
    audit = _load_audit()
    rep = audit.run_audit(ROOT)
    assert rep.errors() == 0, rep.format_text()


def test_audit_strict_gate_logic():
    audit = _load_audit()
    root = _make_root()
    try:
        (root / "apply" / "bad.py").write_text(
            'VARIANTS = ["LaTeX_Resume_CN", "LaTeX_Resume_EN"]\n', encoding="utf-8")
        rep = audit.run_audit(root)
        assert rep.errors() >= 1
    finally:
        shutil.rmtree(root)
