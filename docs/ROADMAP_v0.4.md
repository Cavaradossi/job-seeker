# job-seeker v0.4 — Optimization Plan

> Status: Proposed. Distilled from three strategy rounds (competitor teardown, a
> Claude session, a ChatGPT session) plus the Cursor/Codex skill-mirror sync that
> landed on `main` on 2026-07-15.
>
> Maintainer note: placeholders only. This is a public repo.

## 0. Situation (the uncomfortable truth, with real numbers)

`ai-job-search` (MadsLorentzen) is **not** a peer we can out-build on volume:

| | `ai-job-search` | `job-seeker` (us) |
|---|---|---|
| Stars | **22,710** | 2 |
| Forks | 7,068 | 0 |
| Age | ~4 months | 1 day |
| Topics | 11 | 0 |
| Core dep | **Claude Code (paid)** | pandoc + xelatex + python (free) |

It is a Claude-Code-native "job application framework": JD → AI drafter →
reviewer agent → LaTeX CV + cover letter → ATS check → relevance-weighted
cutting, plus `/scrape` (Danish portals), `/interview`, `/upskill`, salary
benchmarking. Its community flywheel (7k forks, active PRs) is already
self-sustaining.

**Two corrections to the earlier analysis that change the plan:**
1. The competitor's star count is **~6× higher** than early estimates — treat
   its distribution advantage as structural, not transient.
2. Its *core* (`/apply` loop) is country-agnostic; only `/scrape` is Denmark-
   locked. So "they can't be used outside Denmark" is **false** as a moat. The
   only durable, structurally-unreachable moats we have are: **CJK**, **format
   agnosticism**, **honesty-bound positioning**, and **no paid subscription**.

## 1. Strategic Narrative (the one thing everything else serves)

**Do not become "another ai-job-search."** GitHub rarely rewards #2. The goal is
not to beat it — it is that when someone searches *"AI job search GitHub"*,
besides `ai-job-search` they also see `job-seeker` with a clear, distinct
identity.

Proposed one-liner (fits in repo Description ≤ 350 chars):

> **job-seeker** — the offline, honesty-bound resume toolkit for the Chinese-
> speaking world. Bring any resume in any format; get a clean CJK LaTeX / PDF /
> DOCX output. No Claude Code subscription, no scraping, no resume inflation.
> Works with whatever AI editor you already use (Cursor, Codex, WorkBuddy).

This single sentence carries all four moats (CJK, any-format, honesty, free) and
the new multi-agent reality (see §6).

**What we ARE vs what we are NOT**

- ARE: CJK-first · format-agnostic · offline/local · honesty-bound ·
  multi-agent-skill (Cursor + Codex + WorkBuddy).
- ARE NOT: an automated application pipeline · a job-board scraper.

## 2. Guiding principles (from the three rounds)

- **P1 — Narrative over features.** Every feature we add must reinforce the
  one-liner, not dilute it by chasing the competitor's checklist.
- **P2 — Open source is not winner-takes-all.** Next.js/Nuxt, uv/Poetry,
  Claude Code/Codex CLI coexist because each owns a Narrative. We can too.
- **P3 — Community & distribution beat code.** Our acute gap is **0 topics, 0
  badge, 0 community signal** — far more urgent than a missing cover letter.
- **P4 — Borrow relentlessly, name sparingly.** Steal good ideas (portal
  registry, drafter-reviewer, add-portal scaffold). But keep competitor names
  *out* of project docs per GOVERNANCE rule #4 — use neutral "the industry
  moved toward automated pipelines; we chose Y" framing, not an "Inspired by
  ai-job-search" line in the docs tree.
- **P5 — Honesty is the brand.** Anti-inflation rules are a real differentiator
  in an age of AI résumé fakery; make it loud, not buried.

## 3. Prioritized action plan

### P0 — Narrative & discoverability (this week; lowest cost, highest leverage)

1. **Rewrite README first screen.** Add a 30-second "Why job-seeker, not another
   automated job-application framework?" block at the very top — neutral
   comparison, no @-mention of the competitor, anchors on the 4 moats.
2. **One-liner + topics.** Set repo Description to the §1 line. Add ~12 GitHub
   topics (e.g. `resume`, `cv`, `latex`, `cjk`, `chinese`, `markdown`,
   `docx`, `pdf`, `job-application`, `honesty`, `pandoc`, `offline`).
   *(Requires GitHub repo Settings or the `github` connector — currently
   disconnected; flag for the user or reconnect.)*
3. **Architecture diagram.** Put a single overview diagram in README: the
   `convert/` 10-edge any-to-any graph + the `apply/` flow. Star first-impressions
   come from visuals.
4. **star-history badge** in README.
5. **Distribution:** post to r/cscareerquestions, r/ChineseInTech, Hacker News
   (Show HN, timed), 掘金, V2EX, 小红书 (留学/求职). Lead with the overseas-
   Chinese angle (bilingual pain is real for them).

### P1 — `portals.yaml` refactor (next PR; low risk, fits existing adapter pattern)

Claude's best technical idea, and it slots cleanly into our adapter design.

- Add `portals.yaml` (registry): `id`, `name`, `url_patterns`, `regions`,
  `tos_blocks_automation`, `adapter` (points back to an existing Python class).
- Add `resolve_adapter(url)` router in `apply/adapters/__init__.py`; migrate the
  hardcoded `zhipin.com` / `linkedin.com` checks out of `boss_zhipin.py` /
  `linkedin.py` into the yaml. Zero loss of existing function.
- Add `python -m apply --add-portal <url>` scaffold: detect URL pattern, generate
  a yaml entry, run a dry-run. Lowers community PR barrier (great README selling
  point).
- Later: use `regions` for "recommend platforms for my target region" in
  `--setup` (AU → Seek, SG → MyCareersFuture).

### P2 — Cover letter (the real gap)

We have no cover-letter generation; the competitor does. Add:
- A LaTeX cover-letter template + `cover_letter_to_pdf` adapter.
- A `cover_letter` entry in the SKILL variant playbook.

### P3 — Drafter-reviewer via prompt (no code change, no Claude Code lock-in)

Add a "reviewer role" section to `docs/skill/job-seeker/SKILL.md`: after the
drafter produces a variant, a second pass critiques weak phrasing / clichés /
inflation. Pure prompt engineering — model-agnostic, works under Cursor/Codex/
WorkBuddy, and never requires a paid Claude Code subscription. Keep the
rule-based `jd_to_variant` as the free default; LLM tailoring is an optional
enhancement.

### P4 — Honesty as a first-class feature

- Promote the anti-inflation rules from a SKILL note to a visible README section
  + a short "honesty audit" checklist the reviewer pass can run (flags
  unverifiable metrics / title inflation). This is our sharpest brand edge.

> **Implemented (v0.4-dev):** the honesty rules are now a runnable, advisory
> linter — `python -m apply --honesty-check <tex>` (`apply/honesty_check.py`).
> It flags vague superlatives, absolute claims, scope-inflation phrasing
> (honesty boundary §6.1), and bare numbers without a metric verb. The SKILL
> reviewer pass (§4.5) references it. Also shipped an **ATS readability check**
> (`convert/ats_check.py`, wired into `convert --ats-check` and
> `apply --ats-check`) — text-layer / tofu / contact-info / JD-keyword-coverage —
> so "the resume actually parses" is verifiable, not assumed. Both are
> non-blocking and use only existing dependencies (PyMuPDF).

### P5 — Community loop

- Enable GitHub Discussions; triage Issues weekly; showcase notable forks.
- The project is feedback-driven, not code-driven.

## 4. Multi-agent governance (new, from the Cursor/Codex sync)

The 4 synced commits added `.cursor/` and `.codex/` project-skill mirrors, an
`AGENTS.md`, and `scripts/sync_skills.{sh,ps1}`. This is a **strategic asset**:
job-seeker is editor-agnostic across WorkBuddy / Cursor / Codex. To keep it from
rotting (the exact "doc shit-mountain" risk v0.3 governance was built to stop):

- **Single source of truth:** `docs/skill/job-seeker/` is canonical. The
  `.cursor/`, `.codex/`, `.workbuddy/` copies are *generated* mirrors.
- **Sync via script:** `scripts/sync_skills.sh` (and `.ps1`) propagate edits;
  run it after any SKILL change. Add a CI step that fails if a mirror drifts
  from `docs/skill/job-seeker/`.

## 5. Explicit non-goals (scope guardrails)

- **No auto-apply to live portals** — ToS risk + contradicts honesty brand.
  `tos_blocks_automation: true` platforms degrade to "prefill + show", never click.
- **No scraping-engine race** — Boss anti-bot + compliance cost is high; `/scrape`
  stays deferred.
- **No feature-by-feature clone** of the competitor.

## 6. Success metric

Not "more stars than ai-job-search." Success = when someone searches *"AI job
search GitHub"*, `job-seeker` appears alongside it with a one-line identity they
instantly understand: *the offline, honesty-bound, CJK-first, any-format resume
toolkit that works with whatever AI editor they already use.*

---

### Appendix — what the synced Cursor/Codex commits changed (already on `main`)

- `.cursor/skills/job-seeker/` + `.codex/skills/job-seeker/` mirrors (v0.2 SKILL).
- `AGENTS.md` (multi-agent root instructions).
- `scripts/sync_skills.{sh,ps1}` + `scripts/README.md` (mirror sync).
- `docs/skill/` portable source + `CODEX.md` / `CURSOR.md` setup guides.
- `build_resumes.ps1` Windows GBK mojibake fix; `convert/adapters/latex_to_pdf.py`
  + tests tweaks; README bilingual touch-ups.
- Governance verified clean: no `doc/` dir, the upstream template contributor
  acknowledged only in the 3 allowed places (root READMEs + `resume_template/README.md`).
