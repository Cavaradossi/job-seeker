"""Tests for job_seeker.variants (Phase 5 — language-tagged manifests)."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from job_seeker.variants import (
    init_variant,
    read_manifests,
    script_tag_for,
    write_manifest,
)


def test_script_tag_for_maps_common_codes():
    assert script_tag_for("RU", "ru") == "cyrillic"
    assert script_tag_for("AR", "ar") == "arabic"
    assert script_tag_for("HE", "he") == "hebrew"
    assert script_tag_for("JA", "ja") == "cjk"
    assert script_tag_for("EN", "en") == "latin"
    assert script_tag_for("HI", "hi") == "devanagari"
    # unknown suffix falls back to lowercased suffix
    assert script_tag_for("XX") == "xx"


def _scaffold_repo_root() -> Path:
    root = Path(tempfile.mkdtemp())
    tmpl = root / "resume_template"
    tmpl.mkdir()
    (tmpl / "sample.tex").write_text("hello", encoding="utf-8")
    (tmpl / "fonts").mkdir()
    (tmpl / "fonts" / "x.ttf").write_text("x", encoding="utf-8")
    return root


def test_init_variant_creates_dir_and_manifest():
    root = _scaffold_repo_root()
    try:
        target = init_variant("RU", language="ru", root=root)
        assert target.name == "LaTeX_Resume_RU"
        assert (target / "sample.tex").is_file()
        mp = target / "variant.json"
        assert mp.is_file()
        import json
        data = json.loads(mp.read_text(encoding="utf-8"))
        assert data["name"] == "RU"
        assert data["script"] == "cyrillic"
        assert data["language"] == "ru"
        assert data["base_template"] == "resume_template"
    finally:
        shutil.rmtree(root)


def test_read_manifests_lists_tagged_variants():
    root = _scaffold_repo_root()
    try:
        init_variant("RU", language="ru", root=root)
        init_variant("AR", language="ar", root=root)
        manifests = read_manifests(root)
        dirs = {m["_dir"] for m in manifests}
        assert dirs == {"LaTeX_Resume_AR", "LaTeX_Resume_RU"}
        ru = next(m for m in manifests if m["_dir"] == "LaTeX_Resume_RU")
        assert ru["script"] == "cyrillic"
        ar = next(m for m in manifests if m["_dir"] == "LaTeX_Resume_AR")
        assert ar["script"] == "arabic"
    finally:
        shutil.rmtree(root)


def test_write_manifest_roundtrip():
    root = _scaffold_repo_root()
    try:
        d = root / "LaTeX_Resume_TEST"
        d.mkdir()
        p = write_manifest(d, "TEST", "latin", "en")
        import json
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data == {"name": "TEST", "script": "latin",
                        "language": "en", "base_template": "resume_template"}
    finally:
        shutil.rmtree(root)
