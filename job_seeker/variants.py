"""job_seeker/variants.py — language-tagged variant manifests (Phase 5).

Each ``LaTeX_Resume_<SCRIPT>/`` directory may carry a ``variant.json``
declaring its ``{name, script, language, base_template}``. This makes the
script-tagging first-class and machine-readable: a single ``read_manifests()``
call lists every variant the user has, with its writing system — so the
toolkit can surface "you have RU/Cyrillic but no AR/Arabic" rather than just
blind-globbing files.

``init_variant()`` scaffolds a new script dir from ``resume_template/`` with a
prefilled manifest, so adding e.g. ``LaTeX_Resume_RU/`` is one command, not
manual copying. Discovery stays glob-based and backward-compatible: a dir
without a manifest still works; the manifest is purely additive metadata.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]

# Language / suffix code -> canonical script tag used across the toolkit.
# Keeps the manifest's `script` field consistent with detect_script().
_LANG_TO_SCRIPT = {
    "cn": "cjk", "zh": "cjk", "ja": "cjk", "ko": "cjk",
    "en": "latin", "ru": "cyrillic", "uk": "cyrillic",
    "ar": "arabic", "he": "hebrew",
    "hi": "devanagari", "el": "greek",
    "fr": "latin", "de": "latin", "es": "latin", "pt": "latin",
}


def script_tag_for(script_suffix: str, language: Optional[str] = None) -> str:
    """Map a suffix like ``RU`` (or a language code ``ru``) to a script tag."""
    key = (language or script_suffix).lower()
    return _LANG_TO_SCRIPT.get(key, (language or script_suffix).lower())


def manifest_path(script_dir: Path) -> Path:
    return script_dir / "variant.json"


def write_manifest(script_dir: Path, name: str, script: str, language: str,
                   base_template: str = "resume_template") -> Path:
    data = {
        "name": name,
        "script": script,
        "language": language,
        "base_template": base_template,
    }
    p = manifest_path(script_dir)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def read_manifests(root: Path = ROOT) -> list[dict]:
    """List every ``LaTeX_Resume_*/variant.json`` with its metadata.

    Dirs without a manifest are skipped here (glob-based discovery in
    ``variant_renderer`` still finds their .tex files).
    """
    out = []
    for d in sorted(root.glob("LaTeX_Resume_*")):
        if not d.is_dir():
            continue
        mp = manifest_path(d)
        if mp.is_file():
            try:
                data = json.loads(mp.read_text(encoding="utf-8"))
                data["_dir"] = d.name
                out.append(data)
            except Exception:
                pass
    return out


def init_variant(script_suffix: str, language: Optional[str] = None,
                 root: Path = ROOT) -> Path:
    """Scaffold ``LaTeX_Resume_<SCRIPT>/`` from ``resume_template/`` + manifest.

    Copies the template tree (files + subdirs) into the new variant dir if it
    is not already populated, then writes ``variant.json``. The new dir is
    gitignored (private) — same convention as the CN/EN baseline.
    """
    suffix = script_suffix.upper().lstrip("_")
    target = root / f"LaTeX_Resume_{suffix}"
    tmpl = root / "resume_template"
    if not tmpl.is_dir():
        raise FileNotFoundError("resume_template/ not found — run from the repo root")
    target.mkdir(parents=True, exist_ok=True)

    for p in tmpl.iterdir():
        dst = target / p.name
        if p.is_file():
            if not dst.exists():
                shutil.copy2(p, dst)
        elif p.is_dir():
            shutil.copytree(p, dst, dirs_exist_ok=True)

    lang = (language or suffix).lower()
    tag = script_tag_for(suffix, language)
    write_manifest(target, suffix, tag, lang)
    return target


__all__ = ["script_tag_for", "manifest_path", "write_manifest",
           "read_manifests", "init_variant"]
