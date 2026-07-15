---
name: job-seeker
description: >-
  Manages LaTeX resume variants for job applications: tailor bullets to a JD,
  compile PDFs, convert between Markdown/DOCX/PDF/LaTeX, recommend variants,
  run browser-assisted apply (dry-run/rehearse only unless user confirms submit),
  update the application tracker, and enforce honesty boundaries. Use when the
  user mentions 申职器, job-seeker, resume, JD, LaTeX compile, convert resume
  format, apply to a job posting, or tracker updates.
version: 0.2.0
tags: [resume, job-search, latex, career, convert, apply, 申职器]
agent_created: true
---

# job-seeker — 申职器

Workflow skill for multi-variant LaTeX resumes plus format conversion and
browser-assisted application (human-in-the-loop). Enforces honesty boundaries
so bullets never overstate scope, metrics, or titles.

## Editor install paths

| Editor | Path | Notes |
|--------|------|-------|
| **Codex** | `.codex/skills/job-seeker/` + `AGENTS.md` | Committed project Skill + repo-level entry |
| **Cursor** | `.cursor/skills/job-seeker/` | Committed — EN + `SKILL.zh-CN.md` |
| WorkBuddy | `.workbuddy/skills/job-seeker/` | Add `agent_created: true` to frontmatter |
| Portable copy | `docs/skill/job-seeker/` | Mirror for export / generic editors |

Codex setup guide: `docs/skill/CODEX.md`.  
Cursor setup guide: `docs/skill/CURSOR.md`.  
Chinese skill: `SKILL.zh-CN.md` (same directory).  
Windows build: `docs/BUILD_WINDOWS.md` · compile with `.\build_resumes.ps1`.

## When to use

Trigger when the user:

- Pastes a JD and wants a tailored resume or variant recommendation
- Asks to compile / rebuild resume PDFs (`./build_resumes.sh`)
- Wants format conversion (`python -m convert ...`)
- Wants apply dry-run / rehearse (`python -m apply --dry-run ...`)
- Edits `docs/experience_bank.md` or resume `.tex` bullets
- Updates the application tracker after submitting
- Asks whether a bullet violates honesty boundaries
- Asks about 申职器 / job-seeker

Do **not** trigger for generic LaTeX help unrelated to this repo's resume workflow.

## 1. Repo map (relative paths)

```
./                              # job-seeker / 申职器
├── resume_template/            # Public sample template + bundled CJK fonts (always present)
│   └── sample-resume-en_US-zh_CN.tex
├── LaTeX_Resume_CN/            # YOUR private CN variants (create locally; gitignored)
├── LaTeX_Resume_EN/            # YOUR private EN variants (create locally; gitignored)
├── convert/                    # python -m convert — MD/DOCX/PDF/LaTeX any-to-any
├── apply/                      # python -m apply — JD→variant, prefill, confirm gate
├── docs/
│   ├── experience_bank.md      # Private bullet library (gitignored — copy from .example)
│   ├── experience_bank.example.md
│   ├── jd_mapping/             # Private JD notes (gitignored)
│   ├── BUILD_MAC.md
│   └── skill/job-seeker/       # This skill (portable mirror)
├── outputs/                    # Compiled PDFs + tracker (gitignored except README)
├── history/                    # Apply audit logs (gitignored)
├── build_resumes.sh            # macOS/Linux — compiles LaTeX_Resume_* if present
├── build_resumes.ps1           # Windows equivalent
├── scripts/sync_skills.ps1     # Windows — sync skill mirrors
├── scripts/sync_skills.sh      # macOS/Linux — sync skill mirrors
├── .codex/skills/job-seeker/   # Codex project skill
├── AGENTS.md                   # Agent entry (Codex / Cursor / compatible editors)
```

**First-time setup:** copy `resume_template/` files into `LaTeX_Resume_CN/` or
`LaTeX_Resume_EN/`, personalize, then run `./build_resumes.sh`. See root README
Quick start — do not commit personal `.tex` to the public repo.

## 2. Standard workflow

### A. New JD → tailored resume

1. Read JD (pasted text, URL, or `docs/jd_mapping/<company>.md`)
2. Read `docs/experience_bank.md` — **do not invent bullets**
3. Recommend variant: `python -m apply --jd-file <file> --dry-run` or use
   `references/variant_playbook.md`
4. **Plan A (default):** copy general variant `.tex` → change only `\centerline`
   headline → save as `resume-zh_jd_<company>.tex`
5. Build: `./build_resumes.sh` (Windows: `.\build_resumes.ps1`) or compile single file in `resume_template/`
6. Verify page counts in script output — JD variants target **1 page**
7. Update tracker via `apply` audit or manually append
   `outputs/job_application_tracker.csv`

### B. Edit bullets or skills

1. If multi-resume impact, edit `docs/experience_bank.md` first
2. Apply to each affected `LaTeX_Resume_*/*.tex`
3. `./build_resumes.sh` — check `resume_job_en` stays **1 page**

### C. Format conversion

```bash
python -m convert --input path/to/resume.tex --output outputs/resume.pdf
python -m convert --list-routes
```

- **Source of truth for layout:** `.tex → .pdf` via `xelatex`
- LaTeX ↔ DOCX is **lossy** — warn user; macros/icons do not survive
- PDF → Markdown extracts text only (no OCR for scanned PDFs)

Details: `convert/README.md`.

### D. Apply (rehearse / prefill)

```bash
export JOB_SEEKER_NAME="Your Name"
export JOB_SEEKER_EMAIL="you@example.com"
python -m apply --jd-file apply/samples/sample_jd.html --dry-run
python -m apply --url https://example.com/jobs/123 --rehearse
```

**Iron rules:**

- `submit()` always blocks on human `confirm()` — **never auto-submit**
- Boss直聘 / LinkedIn: `tos_blocks_automation=True` → open page + show data only
- Credentials via env vars only — never commit to repo

Details: `apply/README.md`.

### E. After submission

- Tracker row in `outputs/job_application_tracker.csv` (schema: `docs/tracker_schema.md`)
- Optional: `history/apply_<date>.log` via `apply` audit
- Optional: cover note in `outputs/cover_notes/<company>.txt`

## 3. Variant selection

| Variant | Typical source `.tex` | Output PDF | When |
|---------|----------------------|------------|------|
| Sample / demo | `resume_template/sample-resume-en_US-zh_CN.tex` | same dir | First compile, CI |
| CN general | `LaTeX_Resume_CN/resume-zh_job.tex` | `resume_job_cn.pdf` | Domestic dev (1 pg) |
| CN backend/ops | `LaTeX_Resume_CN/resume-zh_backend_ops.tex` | `resume_backend_ops_cn.pdf` | Ops / SRE |
| CN AI/RAG | `LaTeX_Resume_CN/resume-zh_ai_eval.tex` | `resume_ai_eval_cn.pdf` | AI / RAG roles |
| CN JD | `LaTeX_Resume_CN/resume-zh_jd_<co>.tex` | `resume_jd_<co>_cn.pdf` | Headline-only JD |
| EN general | `LaTeX_Resume_EN/resume_job_en.tex` | `resume_job_en.pdf` | English roles (1 pg) |
| EN backend/ops | `LaTeX_Resume_EN/resume_backend_ops.tex` | `resume_backend_ops.pdf` | EN ops |
| EN AI/RAG | `LaTeX_Resume_EN/resume_ai_eval.tex` | `resume_ai_eval.pdf` | EN AI eval |
| Web3 | `LaTeX_Resume_EN/resume_web3.tex` | `resume_web3.pdf` | Anonymous crypto |

Full openers/DM templates: `references/variant_playbook.md`.

## 4. Honesty boundaries

### §4.1 Content authenticity

- No invented metrics — numbers must trace to real work
- No inflated titles (e.g. "Technical Lead" ≠ "Staff Engineer")
- "Maintained/extended existing platform" ≠ "built from scratch"
- ML/retrieval: cite real parameters (TopK, thresholds, chunk strategy)
- POC (few workflow nodes) ≠ "autonomous agent" or production system

### §4.2 Skills-line discipline

- Skills = languages, dev toolchain, general AI productivity tools — short list
- Do **not** put project stacks (RAG, Kafka, etc.) in Skills — put in project bullets
- AI assistants (Cursor, Codex, Trae) are **tools**, not programming languages

### §4.3 Open-source project framing

- Describe side projects by what they actually do — neutral, accurate domain
- GitHub URL on its **own line** (avoid PDF line-wrap overflow)
- Do not reframe a research toolkit as live trading / order routing / signals product

### §4.4 Length

- JD variants + EN general: **1 page** (`enumitem` + tight bullets)
- Full CN with research section: multi-page OK

### §4.5 Drafter–reviewer pass (model-agnostic)

When tailoring a variant to a JD, do **two passes**, not one. This is pure
prompt craft — it works under any editor (Cursor / Codex / WorkBuddy) and
requires no paid subscription or specific model.

1. **Drafter.** Produce the tailored `.tex` variant from the chosen template +
   experience bank, cutting/reweighting bullets for this JD. Keep it honest (§4.1).
2. **Reviewer (separate turn / fresh context).** Re-read ONLY the JD + the
   drafted variant. Critique, do not flatter:
   - Weak verbs, clichés, filler ("utilized", "leveraged", "various").
   - Bullets that read stronger than the underlying work (§4.1 inflation).
   - JD keywords present in name only (keyword-stuffing without substance).
   - Orphans, overflow, >1 page where §4.4 says 1 page.
   - Missing quantification where real numbers exist.
3. **Revise.** Apply only the critiques that keep the bullet truthful. If a
   critique would inflate, reject it and note why.

The reviewer pass is advisory — it never auto-edits. It runs the same honesty
rules as the drafter; its job is to catch what a single pass misses.

## 5. Build & verify

```bash
chmod +x ./build_resumes.sh && ./build_resumes.sh
```

Windows (PowerShell):

```powershell
.\build_resumes.ps1
```

See `docs/BUILD_WINDOWS.md` or `docs/BUILD_MAC.md`.

Critical page-count checks when `LaTeX_Resume_*` exists:

- `resume_job_en.pdf` → **1 page**
- `resume_jd_*_cn.pdf` → **1 page**

If `LaTeX_Resume_CN/` missing, script fails — user must create variants first
or compile `resume_template/` directly with `xelatex`.

Missing `xelatex` → exit 2, see `docs/BUILD_MAC.md`.

## 6. References

| File | When to load |
|------|--------------|
| `references/master_prompt_extract.md` | Full vision + extended rules |
| `references/variant_playbook.md` | Variant pick + opener templates |
| `checklist.md` | Before submit / before PR |
| `docs/skill/CODEX.md` | Codex-specific setup, prompts, MCP boundary |
| `docs/skill/CURSOR.md` | Cursor-specific tips |
| `convert/README.md` | Conversion routes & lossy warnings |
| `apply/README.md` | Apply adapters & confirm gate |

## 7. Placeholders (public repo / examples)

Use `YOUR_NAME`, `your-email@example.com`, `your-org/job-seeker`,
`YOUR_OPEN_SOURCE_PROJECT`, `COMPANY_X` — never real maintainer PII in examples.

## 8. Agent behavior (Codex / Cursor)

1. **Read before write:** `docs/experience_bank.md` + target `.tex`
2. **Minimal diff:** do not refactor `convert/` or `apply/` core unless asked
3. **No silent commit/push** — user must request explicitly
4. **Relative paths only** — no `D:\project\...` or absolute home paths in docs
5. **Verify builds** after `.tex` edits when `xelatex` is available
6. **Apply safety:** default to `--dry-run` / `--rehearse`; live submit only with explicit user `y`

## 9. Out of scope

- Auto-submitting applications without user confirmation
- Committing personal data (real tracker rows, experience bank, private `.tex`)
- OCR for scanned PDFs (not implemented)
- Modifying resume bullets without reading `docs/experience_bank.md`
