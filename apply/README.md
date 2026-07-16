# apply/ — browser-assisted application (Phase 3)

Read a JD URL → recommend a resume variant → prefill the application form →
**PAUSE for human confirmation** → submit → record to the tracker.

## Iron rules (§3 — never violate)

1. **Human-in-the-loop**: `submit()` ALWAYS calls `confirm()` and blocks on its
   return value. It never auto-submits. No exceptions.
2. **One adapter per site**: `boss_zhipin`, `linkedin`, `workday_generic`
   (Workday/Greenhouse/Lever/plain HTML). No monolithic scraper.
3. **Audit log**: every operation appends a row to
   `outputs/job_application_tracker.csv` and a line to `history/apply_<date>.log`.
4. **ToS compliance**: sites whose ToS prohibit automation set
   `tos_blocks_automation = True` → the CLI degrades to "open page + show
   prefill data" (user copies manually). On any automation failure, same degrade.
5. **Credentials**: read from env vars (`JOB_SEEKER_NAME` / `JOB_SEEKER_EMAIL` /
   `JOB_SEEKER_PHONE`) or a `--profile` JSON file. Never stored in the repo.

## Layout

```
apply/
├── adapters/
│   ├── base.py                # SiteAdapter ABC + JDText: read_jd / prefill_form / submit
│   ├── workday_generic.py     # Workday / Greenhouse / Lever / plain HTML (requests + bs4 + Playwright)
│   ├── boss_zhipin.py         # Boss直聘 (tos_blocks_automation=True)
│   ├── linkedin.py            # LinkedIn  (tos_blocks_automation=True)
│   └── registry.py            # resolve_adapter(url) / load_adapter / recommend_platforms — data-driven
├── portals.yaml               # platform registry (id/name/url_patterns/regions/tos/adapter)
├── mapping/
│   ├── jd_to_variant.py       # rule-based JD keywords -> variant name
│   └── variant_renderer.py    # locate .tex -> compile PDF (reuses convert.LatexToPdf)
├── confirm.py                 # the human-in-the-loop gate (blocks; safe in CI)
├── audit.py                   # tracker CSV + history debrief
├── upskill.py                 # --upskill: JD-vs-resume skill-gap analysis
├── cli.py                     # python -m apply ...
├── samples/sample_jd.html     # offline JD for dry-run/rehearse demos
└── tests/                     # 15+ tests, no network/browser needed
```

## Usage

```bash
source .venv/bin/activate

# 1) Dry run — fetch JD + recommend variant + render PDF. No browser, no submit.
python -m apply --jd-file apply/samples/sample_jd.html --dry-run
python -m apply --url https://example.com/jobs/123 --dry-run

# 2) Rehearse the confirmation gate (no browser; demonstrates the §3.1 pause).
python -m apply --jd-file apply/samples/sample_jd.html --rehearse
#   -> blocks at:  [generic] (rehearse) Submit application to ...? [y/N]
#   type n -> rehearse_cancelled (audited); type y -> rehearse_confirmed (audited)

# 3) Live flow — prefill the form, then BLOCK on confirm(), then submit.
#    Requires Playwright:  pip install 'playwright>=1.40' && playwright install chromium
export JOB_SEEKER_NAME="YOUR_NAME"
export JOB_SEEKER_EMAIL="your-email@example.com"
export JOB_SEEKER_PHONE="+86-000-0000-0000"
python -m apply --url https://boards.greenhouse.io/acme/jobs/123 --variant resume_job_en

# Tests
pytest apply/tests/
```

## Platform registry (`portals.yaml` + `--add-portal`)

Routing is **data-driven**, not hard-coded. `portals.yaml` lists every known
platform; `apply/adapters/registry.py` matches a JD URL to the right adapter.

```bash
# List platforms that serve a region (great for overseas applicants):
python -m apply --recommend-platforms AU
#   - LinkedIn (linkedin) [ToS: manual]
#   - Seek (seek)
#   - Indeed Australia (indeed_au) …

# Scaffold a new portal entry (no Python needed to extend):
python -m apply --add-portal https://jobs.lever.co/acme/7
#   (prints the generated YAML entry; add --write-portal to append it)
```

Adding a platform is a YAML edit (or `--add-portal --write-portal`), not a new
Python class — keeping the PR bar low. Only `boss_zhipin` and `linkedin` get
dedicated adapters; everything else uses `GenericAdapter`.

## Skill-gap analysis (`--upskill`)

Given a JD and (optionally) your resume, report the JD keywords your resume is
**missing** — framed as skills to develop. Reuses the same keyword tokenizer as
the ATS check, so the two views stay consistent. Advisory only.

```bash
python -m apply --upskill apply/samples/sample_jd.html
#   Skill-gap analysis (--upskill)
#     coverage: 0% of JD keywords already present
#     [GAP] skills to develop: kubernetes, devops, graphql …

python -m apply --upskill apply/samples/sample_jd.html \
    --resume LaTeX_Resume_EN/sample-resume-en_US-zh_CN.tex
#   coverage: 19% …  [GAP] skills to develop: kubernetes, devops …
```



## ATS readability check (`--ats-check`)

After rendering the variant PDF, run an ATS readability check (text layer,
tofu, contact info) and — because `apply` already read the JD — **JD keyword
coverage** for free. Advisory, non-blocking. See `convert/README.md` for the
full check list.

```bash
python -m apply --jd-file apply/samples/sample_jd.html --variant resume_job_en \
    --dry-run --ats-check
#   ATS readability check
#     file : outputs/resume_job_en_applied.pdf
#     pages: 2  |  text chars: 4391  |  score: 99/100
#     [INFO  ] JD keyword coverage: 47%
#     [INFO  ] Missing keywords: kubernetes, golang, …
```

## Honesty check (`--honesty-check <tex>`)

A heuristic linter that flags resume wording prone to inflating claims —
aligned with the honesty boundaries (checklist.md §E, master_prompt_extract.md
§6.1). Advisory, never auto-edits. Pair it with the SKILL reviewer pass.

```bash
python -m apply --honesty-check LaTeX_Resume_EN/sample-resume-en_US-zh_CN.tex
#   Honesty check (heuristic — advisory, not a verdict)
#     L 12 [uncontextualized-number] 30%
#          → Attach a metric verb (improved/reduced/grew/saved) and a baseline…
#     L 40 [vague-superlative] expert
#          → Replace puffery with a measurable fact; a human reviewer cannot verify…
```

Rules: vague superlatives (expert/guru/ninja/world-class…), absolute claims
(never/always/zero bugs/100% uptime), scope-inflation phrasing (from scratch /
single-handedly / autonomous agent / trading system / live trading), and bare
numbers without a metric verb. Academic "Master" (degree/contest) is **not**
flagged.

## How the human-in-the-loop gate works

`apply/confirm.py::confirm()` is the single chokepoint:

- **Interactive**: blocks on `input("[y/N] ")`. Returns `True` only on explicit `y`/`yes`.
- **Scripted** (CI/tests): `JOB_SEEKER_CONFIRM=yes|no` auto-answers.
- **Non-tty stdin**: defaults to **NO** (never hangs, never silently submits).

`submit()` calls `confirm()` *before* clicking anything. A unit test
(`test_submit_calls_confirm_and_blocks`) asserts the gate is always invoked.

## What runs now vs. what needs Playwright

| Mode | JD fetch | Variant recommend | PDF render | Confirm gate | Form prefill | Real submit |
|------|---------|-------------------|-----------|--------------|--------------|-------------|
| `--dry-run` | ✅ (HTTP / file) | ✅ | ✅ (if variant .tex exists) | — | — | — |
| `--rehearse` | ✅ | ✅ | ✅ | ✅ (blocks) | — | — |
| default (no Playwright) | ✅ | ✅ | ✅ | — | degrades → show data + open browser | — |
| default (Playwright installed, ToS OK) | ✅ | ✅ | ✅ | ✅ (blocks) | ✅ | ✅ (after confirm) |
| default (ToS blocks) | ✅ | ✅ | ✅ | — | degrades → show data + open browser | — |

So the safety-critical path (the confirm gate) and the dry-run are fully
runnable today. True form prefill + submit require Playwright + a ToS-permissive
site; otherwise the tool honestly degrades.

## Variant resolution

`jd_to_variant.recommend_variant(jd)` returns a variant **name** (the `.tex`
stem, matching the SKILL §3 table): `resume_backend_ops`, `resume_ai_eval`,
`resume_web3`, `resume_job_en` (default EN), `resume-zh_job` (default CN).

`variant_renderer.find_variant_tex()` searches `LaTeX_Resume_CN/`,
`LaTeX_Resume_EN/`, then `resume_template/`. The public template repo ships
only the upstream sample (`resume_template/sample-resume-en_US-zh_CN.tex`); add your
own variants to `LaTeX_Resume_*/` in your private fork. If a recommended
variant is missing, the CLI prints a clear note and continues (dry-run still
succeeds).

## Tracker schema

See [`docs/tracker_schema.md`](../docs/tracker_schema.md). Status values written
by `apply`: `dry_run`, `degraded`, `submitted`, `user_cancelled`,
`rehearse_confirmed`, `rehearse_cancelled`. The tracker and `history/` are
gitignored — they hold real company names and dates.
