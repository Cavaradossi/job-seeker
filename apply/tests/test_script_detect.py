import pytest

from apply.mapping.jd_to_variant import (
    Script, detect_script, recommend_variant,
)
from apply.adapters.base import JDText


def _jd(text: str) -> JDText:
    return JDText(url="", title="", company="", location="", raw_text=text, source="test")


def test_detect_script_families():
    assert detect_script("Software engineer with Python and Kubernetes") is Script.LATIN
    assert detect_script("高级后端工程师，熟悉 Kubernetes 与分布式系统") is Script.CJK
    assert detect_script("Ведущий инженер, Python и Kubernetes") is Script.CYRILLIC
    assert detect_script("مهندس برمجيات أول، Python وKubernetes") is Script.ARABIC
    assert detect_script("מהנדס תוכנה בכיר, Python ו-Kubernetes") is Script.HEBREW
    assert detect_script("वरिष्ठ सॉफ्टवेयर इंजीनियर, Python") is Script.DEVANAGARI
    assert detect_script("Ανώτερος μηχανικός λογισμικού, Python") is Script.GREEK


def test_recommend_non_latin_no_longer_forces_cn():
    # A Russian JD (no English keywords) must NOT silently route to the Chinese variant.
    rec = recommend_variant(_jd("Ведущий инженер, проектирование распределённых систем"))
    assert rec.variant == "resume_job_en"          # default base is EN, not CN
    assert rec.warning                            # a clear warning is emitted
    assert "cyrillic" in rec.warning.lower()


def test_recommend_non_latin_honors_preferred_script():
    rec = recommend_variant(
        _jd("مهندس برمجيات أول، تطوير واجهات الويب"), preferred_script="zh")
    assert rec.variant == "resume-zh_job"
    assert rec.warning
    assert "arabic" in rec.warning.lower()


def test_recommend_latin_and_cjk_still_route_correctly():
    assert recommend_variant(_jd("Marketing manager, communications and brand")).variant == "resume_job_en"
    assert recommend_variant(_jd("产品设计师，用户体验与交互")).variant == "resume-zh_job"


def test_recommend_keyword_rules_win_over_script():
    rec = recommend_variant(_jd("AI eval engineer, RAG and LLM benchmarking"))
    assert rec.variant == "resume_ai_eval"
    assert rec.warning == ""
