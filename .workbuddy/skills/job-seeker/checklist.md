# Checklist — 申职器 (job-seeker)

Use this checklist before, during, and after editing resumes or submitting applications.

---

## A. Before editing a resume

- [ ] Read `doc/experience_bank.md` for the relevant bullets
- [ ] Read the target `.tex` file in full
- [ ] Identify the variant (job / JD-specific / ai_eval / backend_ops / web3 / CN-full)
- [ ] If new JD: read `doc/jd_mapping/<company>.md` or the pasted JD
- [ ] Decide Plan A (headline-only change) vs Plan B (deeper edit)

## B. While editing

- [ ] Use `./` relative paths in any new content (never `D:\project\...`)
- [ ] Skills section discipline:
  - [ ] No RAG stack / Agent workflow buzzwords in Skills
  - [ ] No "Engineering" mashup with pytest/Kafka
  - [ ] Codex/Cursor/Trae listed as AI tools, **not** as programming languages
- [ ] Open-source project framing (§6.3 of master prompt):
  - [ ] Title matches "Open-Core Research Workflow Framework" (or CN equivalent)
  - [ ] GitHub URL on its own line, not crowded into a long bullet
  - [ ] No claims of: live trading, order routing, market-specific, signals product
- [ ] Honesty boundaries (§6.1):
  - [ ] No invented metrics — every number traces to real work
  - [ ] Title is "Technical Lead" (lifecycle), not "Architect" / "Staff"
  - [ ] ETL described as "developed & maintained PDI on existing platform", not "greenfield"
  - [ ] Dify described as "Workflow POC (4–5 nodes)", not "Autonomous Agent"

## C. After editing, before submitting

- [ ] Ran `./build_resumes.sh` successfully (exit code 0)
- [ ] Page counts in the summary table match expectations:
  - [ ] `resume_job_en.pdf` is **1 page** (acceptance criterion)
  - [ ] All `resume_jd_*_cn.pdf` are 1 page
  - [ ] `resume-zh_CN.pdf` may be multi-page (full version)
- [ ] No `.tex` / `resume.cls` / fontawesome copies leaked into `outputs/`
- [ ] Build artifacts (`*.aux`, `*.log`, `*.out`, `*.pdf`) cleaned from `LaTeX_Resume_*/`
- [ ] PDF opens correctly (icons render, no missing-font warnings)
- [ ] GitHub link in PDF is clickable and on its own line
- [ ] No real email/phone leaked into example content (use `your-email@example.com` for skill mirrors)

## D. After submitting an application

- [ ] Appended a row to `outputs/job_application_tracker_domestic.csv` (or international tracker)
- [ ] Company name, role, date, variant used, JD source, status columns filled
- [ ] Optional: saved the JD text to `doc/jd_mapping/<company>.md` for future reference
- [ ] Optional: wrote a cover note in `outputs/cover_notes/<company>.txt`
- [ ] Optional: debrief entry in `history/job_search_2025_2026.md`

## E. Honesty self-audit (before any submit)

Walk through each bullet in the resume you're about to send and ask:

1. **Did I actually do this?** (If "kind of" — reword or remove.)
2. **Was the metric mine or the team's?** (If team's — say "team" or reframe to your scope.)
3. **Did I hold this title?** (If aspirational — use the real title.)
4. **Is the timeframe accurate?** (No fudged start/end dates.)
5. **Does this overstate the scope?** (POC vs production, greenfield vs maintenance, lead vs IC.)
6. **Is the open-source project described truthfully?** (No "trading system" if it's a research-workflow toolkit.)

If any answer is "no" or "kind of" — fix the bullet before submitting. Do not submit a resume with known honesty violations.

## F. Open-source contribution checklist (when editing the public repo)

- [ ] No real name / email / GitHub in example content (use `YOUR_NAME`, `your-email@example.com`, `your-org/job-seeker`)
- [ ] No real company names in JD examples (use `COMPANY_X`)
- [ ] No real metrics in `experience_bank.example.md` (use `METRIC_N`)
- [ ] `outputs/`, `history/`, `meessage/`, `doc/jd_mapping/`, `doc/*.docx` are gitignored
- [ ] Commit does not include `.aux`, `.log`, `.out`, or compiled PDFs in `LaTeX_Resume_*/`
