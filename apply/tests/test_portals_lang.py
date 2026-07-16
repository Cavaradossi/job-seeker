import pytest

from apply.adapters.registry import recommend_platforms, add_portal, PORTALS_PATH
import yaml


def _portals():
    data = yaml.safe_load(PORTALS_PATH.read_text(encoding="utf-8"))
    return data.get("platforms", [])


def test_recommend_by_region_still_works():
    hits = recommend_platforms("CN")
    ids = {p["id"] for p in hits}
    assert {"boss_zhipin", "liepin", "job51"}.issubset(ids)


def test_recommend_by_language():
    # Language-based discovery: 'zh' must surface the Chinese portals (+ SG bilingual).
    zh = recommend_platforms("zh")
    ids = {p["id"] for p in zh}
    assert "boss_zhipin" in ids
    assert "mycareersfuture" in ids       # SG is bilingual [en, zh]


def test_recommend_by_script():
    # Script-based discovery: 'latin' surfaces the Latin-script portals.
    latin = recommend_platforms("latin")
    assert latin  # at least the global / EN portals
    assert all("latin" in [s.lower() for s in p.get("scripts", [])] for p in latin)


def test_add_portal_emits_languages_scripts():
    entry = add_portal("https://emploi.example.ma/jobs/1",
                       languages=["fr", "ar"], scripts=["latin", "arabic"])
    assert "languages" in entry and entry["languages"] == ["fr", "ar"]
    assert "scripts" in entry and entry["scripts"] == ["latin", "arabic"]
    # Without them, the keys are omitted (clean default entry).
    plain = add_portal("https://example.com/x")
    assert "languages" not in plain
    assert "scripts" not in plain
