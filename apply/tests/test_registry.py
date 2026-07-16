import pytest

from apply.adapters.registry import (
    resolve_adapter, recommend_platforms, add_portal, load_adapter,
)


def test_resolve_known_platforms():
    assert resolve_adapter("https://www.zhipin.com/job/1")["id"] == "boss_zhipin"
    assert resolve_adapter("https://www.linkedin.com/jobs/view/9")["id"] == "linkedin"
    # substring match, case-insensitive
    assert resolve_adapter("HTTPS://BOARDS.GREENHOUSE.IO/acme")["id"] == "greenhouse"
    assert resolve_adapter("https://seek.com.au/jobs/3")["id"] == "seek"


def test_resolve_unknown_falls_back_to_generic():
    p = resolve_adapter("https://some-unknown-board.example/x")
    assert p["id"] == "unknown"
    assert p["adapter"] == "generic"


def test_load_adapter_returns_instance():
    from apply.adapters.base import SiteAdapter
    assert isinstance(load_adapter("boss_zhipin"), SiteAdapter)
    assert isinstance(load_adapter("linkedin"), SiteAdapter)
    assert isinstance(load_adapter("generic"), SiteAdapter)
    # unknown key -> generic fallback
    assert isinstance(load_adapter("does-not-exist"), SiteAdapter)


def test_recommend_platforms_by_region():
    au = {p["id"] for p in recommend_platforms("AU")}
    assert "seek" in au and "indeed_au" in au
    # global platforms appear for any region
    assert "linkedin" in au
    cn = {p["id"] for p in recommend_platforms("CN")}
    assert "boss_zhipin" in cn
    # unknown region still returns global platforms
    assert "linkedin" in {p["id"] for p in recommend_platforms("ZZ")}


def test_add_portal_builds_entry():
    e = add_portal("https://jobs.lever.co/acme/7")
    assert e["id"] == "lever"
    assert e["url_patterns"] == ["jobs.lever.co"]
    assert e["adapter"] == "generic"
    # host with subdomain -> take the second-level label
    assert add_portal("https://myworkdayjobs.com/acme")["id"] == "myworkdayjobs"
