# job-seeker — 申职器

Open-source resume management toolkit: LaTeX template + cross-platform build scripts + Agent Skill for tailoring resumes to job descriptions.

> **Status**: v0.1 — template + build scripts + Skill skeleton. Format conversion (Phase 2) and browser-assisted application (Phase 3) are planned.

## What's in this repo

| Path | What |
|------|------|
| `resume_template/` | Clean LaTeX resume template (upstream: billryan/HouJP). Ships with bundled fonts — no system font install needed. |
| `build_resumes.sh` | macOS/Linux build script (xelatex + page-count reporting). Reference implementation — adapt to your directory structure. |
| `build_resumes.ps1` | Windows build script (PowerShell, equivalent behavior). |
| `doc/BUILD_MAC.md` | How to install TeX Live on macOS (MacTeX, BasicTeX, or user-level without sudo). |
| `doc/job_seeker_opensource_plan.md` | Full open-source plan: scope, privacy strategy, 3-phase roadmap. |
| `doc/experience_bank.example.md` | Template for your bullet material library (placeholders only). |
| `doc/tracker_schema.md` | Application tracker CSV column definitions. |
| `docs/skill/job-seeker/` | Portable Agent Skill (editor-agnostic). Import into WorkBuddy, Cursor, or use manually. |
| `.workbuddy/skills/job-seeker/` | WorkBuddy-native Skill (auto-loads when you clone this repo in WorkBuddy). |
| `.github/workflows/build-resumes.yml` | CI: compiles the template sample on push/PR. |

## Quick start

### 1. Install TeX

See [`doc/BUILD_MAC.md`](doc/BUILD_MAC.md) for full instructions. Short version (macOS with Homebrew):

```bash
brew install --cask mactex
```

### 2. Compile the sample

The template ships with a sample `.tex` file:

```bash
cd resume_template
xelatex -interaction=nonstopmode HouJP-en_US-zh_CN.tex
# → produces HouJP-en_US-zh_CN.pdf
```

### 3. Create your own resume variants

1. Copy `resume_template/` to `LaTeX_Resume_CN/` (or `LaTeX_Resume_EN/`)
2. Rename and customize the `.tex` file (replace `YOUR_NAME`, `your-email@example.com`)
3. Create `doc/experience_bank.md` from the [example template](doc/experience_bank.example.md)
4. Adapt `build_resumes.sh` to your file list (edit the `CN_FILES` and `EN_FILES` arrays)
5. Run `./build_resumes.sh` to compile all variants

### 4. Use the Agent Skill

The Skill teaches an AI agent the resume-editing workflow: read experience bank → edit `.tex` → compile → check page count → update tracker.

- **WorkBuddy**: the skill at `.workbuddy/skills/job-seeker/` auto-loads. Just start chatting.
- **Cursor**: copy `docs/skill/job-seeker/` to `.cursor/skills/job-seeker/`.
- **Other editors**: see [`docs/skill/job-seeker/README.md`](docs/skill/job-seeker/README.md) for import instructions.

## Honesty boundaries

The Skill enforces honesty rules to prevent resume inflation:

- **§6.1 Content authenticity**: no invented metrics, no inflated titles
- **§6.2 Skills-line discipline**: no RAG/Agent buzzwords in Skills section
- **§6.3 Source honesty**: describe projects truthfully, don't anchor on any single one
- **§6.4 Length**: JD-specific variants target 1 page; full versions may be multi-page

See [`docs/skill/job-seeker/SKILL.md`](docs/skill/job-seeker/SKILL.md) §4 for the full rules.

## Roadmap

| Phase | Status | Scope |
|-------|--------|-------|
| **Phase 1** | ✅ v0.1 | Cross-platform build + Skill skeleton + open-source plan |
| **Phase 2** | 📋 planned | Format conversion: Markdown ↔ DOCX ↔ PDF ↔ LaTeX (pandoc + python-docx, adapter pattern) |
| **Phase 3** | 📋 planned | Browser auto-application: read JD → prefill form → human-in-the-loop submit (Playwright, site adapters) |

Full plan: [`doc/job_seeker_opensource_plan.md`](doc/job_seeker_opensource_plan.md).

## License

MIT — see [`LICENSE`](LICENSE).

The `resume_template/` directory is derived from the [billryan/RUC-Thesis](https://github.com/billryan/resume) template (also MIT). All bundled fonts retain their original licenses.

## Contributing

This is an early-stage project. Issues and PRs are welcome once the repo is public. For now, see the [open-source plan](doc/job_seeker_opensource_plan.md) for the direction.
