import pytest

from apply.upskill import analyze, run_upskill


def _jd():
    return ("We need a senior backend engineer with Python, Kubernetes, and "
            "DevOps experience. Strong SQL and CI/CD skills required.")


def _resume():
    return "Backend engineer experienced with Python and SQL. Built CI/CD pipelines."


def test_analyze_coverage_and_gap():
    rep = analyze(_jd(), _resume(), jd_source="jd", resume_source="r")
    # 'python' and 'sql' and 'cicd' should be present
    present = {t.lower() for t in rep.present}
    assert "python" in present and "sql" in present
    # kubernetes / devops should be in the gap
    gap = {t.lower() for t in rep.gap}
    assert "kubernetes" in gap and "devops" in gap
    assert 0.0 < rep.coverage < 1.0


def test_analyze_no_resume_reports_full_gap():
    rep = analyze(_jd(), None, jd_source="jd")
    assert rep.coverage == 0.0
    assert rep.gap  # every JD keyword is a gap


def test_analyze_empty_jd_is_safe():
    rep = analyze("", _resume())
    assert rep.coverage == 1.0
    assert rep.gap == []


def test_run_upskill_local_html(tmp_path):
    jd = tmp_path / "jd.html"
    jd.write_text(
        "<html><body><h1>Role</h1><p>Need Python and Kubernetes.</p></body></html>",
        encoding="utf-8",
    )
    rep = run_upskill(str(jd))
    assert rep.jd_source.endswith("jd.html")
    # HTML tag names (html/body/h1/p) must NOT leak into the gap
    gap = {t.lower() for t in rep.gap}
    assert "html" not in gap and "body" not in gap and "p" not in gap
    assert "python" in gap and "kubernetes" in gap


def test_run_upskill_with_resume(tmp_path):
    jd = tmp_path / "jd.txt"
    jd.write_text("Requires Python, Kubernetes, and GraphQL.", encoding="utf-8")
    resume = tmp_path / "r.txt"
    resume.write_text("Python developer with GraphQL experience.", encoding="utf-8")
    rep = run_upskill(str(jd), str(resume))
    assert rep.coverage > 0.0
    gap = {t.lower() for t in rep.gap}
    assert "kubernetes" in gap          # wanted, not in resume
    assert "python" not in gap          # present in resume
    assert "graphql" not in gap          # present in resume
