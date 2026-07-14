---
name: job-seeker
description: This skill should be used when editing resumes for a new job description, compiling resume PDFs, updating the application tracker, or checking honesty boundaries before submission. Covers the 申职器 (job-seeker) workflow from experience bank to compiled PDF.
agent_created: true
version: 0.1.0
tags: [resume, job-search, latex, career,申职器]
---

# job-seeker — 申职器 Resume Workflow Skill

A workflow skill for managing multi-variant LaTeX resumes: pick a variant for a given JD, edit the `.tex`, compile to PDF, verify page count, and update the tracker. Enforces honesty boundaries so bullets never overstate scope, metrics, or titles.

This skill is project-scoped — it lives in `.workbuddy/skills/job-seeker/` of the `seeking_job` repo and travels with the repository.

## When to use

Trigger this skill when the user:

- Pastes a new job description and asks for a tailored resume
- Asks to compile / build / regenerate resume PDFs
- Wants to add or edit a bullet in `doc/experience_bank.md`
- Asks to "update the tracker" after submitting an application
- Wants to verify honesty boundaries before submitting (e.g. "is this bullet OK?")
- Asks about the 申职器 / job-seeker project itself

Do **not** trigger this skill for general LaTeX questions unrelated to this repo's resume variants.

## 1. Repo map (all relative paths)

```
./                                # repo root (seeking_job / 申职器 prototype)
├── LaTeX_Resume_CN/              # Chinese resume sources (xelatex + zh_CN-Adobefonts)
│   ├── resume.cls                # local document class (builds on article)
│   ├── zh_CN-Adobefonts_external.sty  # CJK font config (loads bundled .otf)
│   ├── linespacing_fix.sty
│   ├── resume-zh_CN.tex          # full CN version (multi-page, includes research)
│   ├── resume-zh_job.tex         # CN general (1 page)
│   ├── resume-zh_backend_ops.tex # CN backend/ops variant
│   ├── resume-zh_ai_eval.tex     # CN AI/RAG variant
│   └── resume-zh_jd_<company>.tex # JD-specific CN variants (headline-only diffs)
├── LaTeX_Resume_EN/              # English resume sources (xelatex, no CJK)
│   ├── resume.cls
│   ├── resume_job_en.tex         # EN general (1 page)
│   ├── resume_backend_ops.tex
│   ├── resume_ai_eval.tex
│   └── resume_web3.tex           # Web3 anonymous variant
├── resume_template/              # upstream billryan/HouJP clean template (no personal info)
├── doc/
│   ├── experience_bank.md        # bullet material library — READ FIRST before editing .tex
│   ├── jd_mapping/               # JD summaries & keywords per company
│   └── BUILD_MAC.md              # macOS TeX install instructions
├── outputs/                      # compiled PDFs + tracker + cover notes (gitignored except README)
├── history/                      # interview & application records (private)
├── build_resumes.sh              # macOS/Linux build script
├── build_resumes.ps1             # Windows build script (equivalent behavior)
└── .github/workflows/build-resumes.yml  # CI: compile on push/PR
```

## 2. Standard workflow

### A. New JD → tailored resume

1. Read the JD (user-pasted text or `doc/jd_mapping/<company>.md`)
2. Read `doc/experience_bank.md` to pick bullets — **do not invent**
3. Default to **Plan A**: copy `resume-zh_job.tex` → only change the `\centerline` headline → save as `resume-zh_jd_<company>.tex`
4. Build: `./build_resumes.sh`
5. Verify page count from the script's summary table — JD variants must be 1 page
6. Update `outputs/job_application_tracker_domestic.csv` and `outputs/cover_notes/<company>.txt`

### B. Edit bullets or skills

1. If the change affects multiple resumes, edit `doc/experience_bank.md` first
2. Apply the same edit to each affected `LaTeX_Resume_*/*.tex`
3. Run `./build_resumes.sh` and check page counts — especially `resume_job_en.pdf` (must stay 1 page)

### C. After submission

- Append a row to `outputs/job_application_tracker_domestic.csv` (or the international tracker)
- Optional: write a debrief in `history/job_search_2025_2026.md`

## 3. Variant selection table

| Variant | Source `.tex` | Output PDF | When to use |
|---------|---------------|------------|-------------|
| CN full | `LaTeX_Resume_CN/resume-zh_CN.tex` | `resume-zh_CN.pdf` | Multi-page version with research, for senior/academic-leaning roles |
| CN general | `LaTeX_Resume_CN/resume-zh_job.tex` | `resume_job_cn.pdf` | Default for domestic dev roles (1 page) |
| CN backend/ops | `LaTeX_Resume_CN/resume-zh_backend_ops.tex` | `resume_backend_ops_cn.pdf` | Backend / SRE / ops roles |
| CN AI/RAG | `LaTeX_Resume_CN/resume-zh_ai_eval.tex` | `resume_ai_eval_cn.pdf` | AI eval, RAG, LLM application roles |
| CN JD-specific | `LaTeX_Resume_CN/resume-zh_jd_<company>.tex` | `resume_jd_<company>_cn.pdf` | Headline-only customization for a specific company |
| EN general | `LaTeX_Resume_EN/resume_job_en.tex` | `resume_job_en.pdf` | Overseas / English-speaking roles (1 page) |
| EN backend/ops | `LaTeX_Resume_EN/resume_backend_ops.tex` | `resume_backend_ops.pdf` | English backend/ops roles |
| EN AI/RAG | `LaTeX_Resume_EN/resume_ai_eval.tex` | `resume_ai_eval.pdf` | English AI eval/benchmark roles |
| Web3 | `LaTeX_Resume_EN/resume_web3.tex` | `resume_web3.pdf` | Anonymous (pseudonym) for crypto/Web3 |

Full variant guidance including openers and DM templates: see `references/variant_playbook.md`.

## 4. Honesty boundaries (thematic — from master prompt §6)

> The original master prompt labels these "G1–G6" but the actual rules are organized thematically as §6.1–§6.4. Use the thematic structure, not a fabricated numbered list.

### §6.1 Content authenticity

- Do not invent metrics. Numbers in bullets must come from real work.
- Do not inflate titles. Use the actual role title (e.g. "Technical Lead" managing a software lifecycle) — not "Architect" or "Staff Engineer".
- Describe scope accurately: "maintained and extended an existing platform" — not "built it from scratch".
- For any ML / retrieval work, cite the real parameters you actually used (e.g. TopK, similarity threshold, chunk strategy); do not claim capabilities not implemented.
- Distinguish a small POC (a few connected nodes/steps) from a production "autonomous agent" — don't inflate a prototype into a system.

### §6.2 Skills-line discipline

- Skills section lists **languages, dev toolchain, and general-purpose productivity tools** only — kept short and scannable.
- Do **not** put project-specific tech stacks, domain frameworks, or workflow architectures in Skills — those belong in the relevant project bullet where the context lives.
- Do **not** pass off AI coding assistants or editors as programming languages (list them as tools, if at all — never where a language belongs).
- Treat the Skills line as a keyword index recruiters skim, not a place to signal seniority or niche expertise.

### §6.3 Source honesty (project framing)

- When referencing personal open-source projects, describe them by what they actually do — not aspirationally.
- Do not anchor the resume on any single side project; it is one of multiple data points.
- Pick a neutral, accurate descriptor and avoid inflating scope or domain (don't reframe a small tool as a "platform", "system", or "product" unless it truly is).
- Cite the real GitHub URL on its own line; don't crowd it into a long bullet (prevents PDF line-wrap issues).

### §6.4 Length

- CN JD-specific variants: target **1 page** (use `enumitem` to compress itemize).
- EN `resume_job_en`: target **1 page** (compress bullet wording + `enumitem`).
- CN full `resume-zh_CN`: multi-page is OK (includes research section).

## 5. Build & verify

```bash
chmod +x ./build_resumes.sh
./build_resumes.sh
```

The script prints a page-count table at the end. Critical checks:

- `resume_job_en.pdf` must be **1 page** (acceptance criterion)
- All JD variants must be **1 page**
- `resume-zh_CN.pdf` may be multi-page

If `xelatex` is missing, the script exits with code 2 and points to `doc/BUILD_MAC.md`.

## 6. References

| Reference | Path | When to load |
|-----------|------|--------------|
| Master prompt extract | `references/master_prompt_extract.md` | When you need the full honesty rules or product vision |
| Variant playbook | `references/variant_playbook.md` | When picking a variant or writing an opener/DM |
| Checklist | `checklist.md` | Before submitting any application |
| Build script | `scripts/build_resumes.sh` (symlink to `../../../../build_resumes.sh`) | When compiling |

## 7. Placeholders (for open-source / skill examples)

When generating **example** content for the open-source mirror (`docs/skill/job-seeker/`), always use placeholders:

- Name: `YOUR_NAME`
- Email: `your-email@example.com`
- GitHub: `your-org/job-seeker`
- Project name: `YOUR_OPEN_SOURCE_PROJECT`

Never write the maintainer's real name, real email, or real GitHub into example content.

## 8. Out of scope

This skill does **not**:

- Auto-submit job applications (Phase 3, human-in-the-loop only)
- Convert between Markdown / DOCX / PDF / LaTeX (Phase 2)
- Push to public GitHub repos without explicit user confirmation
- Modify `.tex` body content without first reading `doc/experience_bank.md`
