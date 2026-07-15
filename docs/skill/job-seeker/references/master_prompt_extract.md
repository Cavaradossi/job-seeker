# Master Prompt Extract — 申职器 (job-seeker) Reference

> Condensed from `docs/work_buddy_master_prompt.md`. Personal identifiers replaced with placeholders. This is a reference, not the source of truth — for the full prompt, read the original.

---

## 1. Identity & context

- **Maintainer**: `YOUR_NAME`
- **Email**: `your-email@example.com`
- **GitHub (open source)**: `your-org/job-seeker`
- **Experience level**: ~3 years (adjust to actual)
- **Role framing**: Technical Lead (software lifecycle) — **not** Architect / Staff
- **Preferences**: remote-first; short onsite acceptable

## 2. Repo map (relative paths)

See `SKILL.md` §1. All commands use `./` relative paths — never absolute Windows paths like `D:\project\...`.

External read-only code (not in this repo, references only — do not write private repo paths into resumes):

- Sibling `../YOUR_OPEN_SOURCE_PROJECT` — public main repo
- (Private forks kept private — never expose)

## 3. Product vision: 申职器 / job-seeker

This repo is the MVP of **申职器 (job-seeker)**. Long-term goal:

### 3.1 MVP (current)

- Multi-variant LaTeX resume sources + one-command compile to `outputs/`
- `experience_bank.md` unifies bullet material and honesty boundaries
- JD mapping + customized headlines (Plan A: same body, only headline differs)
- Tracker CSV, cover notes, variant playbook

### 3.2 Planned (by priority)

| Capability | Notes |
|------------|-------|
| Format conversion | Markdown ↔ DOCX ↔ PDF ↔ LaTeX; single "source document" → multi-format export |
| Browser auto-application | Playwright or IDE Browser: read JD → pick variant → prefill form → upload PDF → record to tracker (**requires explicit user confirmation before submit**) |
| Open-source extraction | Extract `experience_bank`, build scripts, JD templates, tracker schema into standalone repo or Skill (package name `job-seeker`, CN name `申职器`) |
| Skill publishing | `SKILL.md` covers: edit resume, compile, application opener, honesty boundary checklist |
| Cross-platform build | `build_resumes.sh` (macOS/Linux) + `build_resumes.ps1` (Windows) |
| CI | GitHub Actions: compile PDF artifact on push |

### 3.3 Auto-application design principles (when implemented)

1. **Human-in-the-loop**: prefill OK; final "submit" click requires explicit user confirmation.
2. **Site adapters**: one adapter per recruiting site (Boss, Lagou, official career pages). No monolithic scraper.
3. **Audit log**: every operation writes to `history/` or tracker columns (timestamp, site, PDF used, success).
4. **Anti-crawl & ToS**: respect site terms; on failure, degrade to "open page + prefill fields".
5. **Sensitive info**: no credentials in repo; use env vars or system keychain.

## 4. Resume variants & selection

See `SKILL.md` §3 for the table. Full openers and DM templates in `references/variant_playbook.md`.

## 5. Compile (macOS)

```bash
chmod +x ./build_resumes.sh
./build_resumes.sh
```

Pre-requisites: `xelatex` (MacTeX or TeX Live) + CJK font packages matching `zh_CN-Adobefonts_external`. See `docs/BUILD_MAC.md` for full install instructions.

**Iron rule**: `outputs/` only holds PDFs and tracker/notes — **never** copy `.tex` / `resume.cls` into `outputs/`.

## 6. Writing & layout rules (honesty boundaries)

> The original prompt labels this section "G1–G6 + extensions" but the actual rules are thematic §6.1–§6.4. Use thematic structure.

### 6.1 Global honesty

- ~3 years experience; Open API **Technical Lead** = managing software engineering lifecycle, **not** "independently developed all APIs".
- ETL: developed & maintained multiple PDI on existing platform — **not** greenfield from scratch.
- RAG: write real retrieval params (TopK, similarity threshold, chunk + JSON/Markdown).
- Dify: **Workflow POC** (4–5 nodes) — **not** Autonomous Agent.
- Personal open-source project: describe by what it actually does (e.g. "open-core framework for reproducible research workflows"); **do not** call it a trading system, live trading framework, or market-specific toolkit.

### 6.2 Skills-line discipline (final)

| Variant | Skill structure |
|---------|-----------------|
| job / JD | Languages: Python/SQL/Bash/C++; Tools: Git/SVN/Jira + AI tools (Codex/Cursor/Trae) |
| ai_eval | Languages + LaTeX; **AI skills** Cursor/Codex/Trae; **Dev toolchain** Git/Linux/SVN/Jira (don't mix "Engineering" with pytest/Kafka) |
| backend_ops | Languages/scripts; Oracle; collaboration Git/SVN/Jira; **AI skills** Cursor/Codex/Trae (ops roles also showcase AI efficiency) |

Do **not**: put RAG stack in Skills; put Agent workflows in Skills; write Codex as a "programming language".

### 6.3 Personal open-source project framing

- **EN title**: `YOUR_OPEN_SOURCE_PROJECT — Open-Core Research Workflow Framework`
- **CN title**: `YOUR_OPEN_SOURCE_PROJECT — 开源研究工作流框架`
- Bullets: internal research workflow abstraction → recipe chain → staged JSON/CSV artifacts + schema ID → extension-pack boundary → artifact audit / golden test / parity → PyPI
- GitHub URL on its own line (not crowded into a long bullet — prevents PDF line wrap)
- **Do not write**: live trading, order routing, market-specific, signals product

### 6.4 Length

- CN JD-specific variants: target **1 page** (use `enumitem` to compress itemize)
- EN `resume_job_en`: target **1 page** (compress bullet wording + `enumitem`)
- CN full `resume-zh_CN`: multi-page OK (includes research)

## 7. Standard workflow

### A. New JD → tailored resume

1. Read `docs/jd_mapping/` or user-pasted JD
2. Cross-reference `docs/experience_bank.md` for bullets — **do not exaggerate**
3. Default Plan A: copy `resume-zh_job.tex` → only change `\centerline` headline → output `resume-zh_jd_<company>.tex`
4. Compile → `outputs/resume_jd_*_cn.pdf`
5. Update `outputs/job_application_tracker_domestic.csv` and `outputs/cover_notes/`

### B. Edit bullets / skills

1. Edit `docs/experience_bank.md` first (if affecting multiple resumes)
2. Apply edits to each affected `LaTeX_Resume_*/*.tex`
3. Compile and **check page count** (especially `resume_job_en.pdf`)

### C. Application records

- Tracker: `outputs/job_application_tracker_domestic.csv` (or international variant)
- Debrief: `history/job_search_2025_2026.md`

### D. Refresh facts from docx

```bash
python docs/extract_docx.py
```

## 8. Agent behavior rules

1. **Read before write**: read `experience_bank.md` and the target `.tex` before editing.
2. **Minimal diff**: only touch files relevant to the task; do not auto-commit unless user asks.
3. **Compile verification**: after editing `.tex`, run xelatex and report page count.
4. **Paths**: use `./` relative paths on macOS; never `D:\project\...`.
5. **Open-source evolution**: repetitive ops (JD → resume → PDF → tracker) should be considered for extraction into a 申职器 module or Skill.
6. **Auto-application**: do not pretend to submit before the feature exists; when it exists, start with "open page + snapshot + prefill" only.

## 9. Quick checklist (after editing resume)

- [ ] PDF page count matches expectation (job_en / JD = 1 page)
- [ ] Open-source project title & bullets match §6.3
- [ ] GitHub link not crowded into a long line
- [ ] Skills section has no RAG stack / no "Engineering" mashup
- [ ] Honesty boundaries respected (§6.1)
- [ ] `outputs/` updated with PDF, no stray `.tex`
