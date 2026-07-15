# Using job-seeker with Cursor

Cursor loads **project skills** from `.cursor/skills/`. This repo ships the skill
pre-installed — clone, open the folder in Cursor, and the agent can follow the
申职器 workflow.

## Quick setup

1. Clone and open the repo in Cursor.
2. Confirm `.cursor/skills/job-seeker/SKILL.md` exists (committed with the project).
3. Copy your private material locally (never commit):
   - `docs/experience_bank.example.md` → `docs/experience_bank.md`
   - `resume_template/` → `LaTeX_Resume_CN/` and/or `LaTeX_Resume_EN/` (personalize)
4. Install tools: `xelatex`, Python 3.10+, optional `pandoc` and Playwright
   - **Windows:** [`docs/BUILD_WINDOWS.md`](../BUILD_WINDOWS.md) (MiKTeX + PowerShell)
   - **macOS / Linux:** [`docs/BUILD_MAC.md`](../BUILD_MAC.md)
5. Python venv + deps:

   **Windows (PowerShell)**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   **macOS / Linux**

   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

6. Optional: read root [`AGENTS.md`](../AGENTS.md) — agent entry + hard rules.
7. Editing `*.tex` triggers [`.cursor/rules/resume-editing.mdc`](../../.cursor/rules/resume-editing.mdc).

## How to invoke the skill

Cursor picks skills from the `description` field in frontmatter. You can also
steer explicitly:

- 「用申职器 Skill，根据这份 JD 改简历」
- 「compile resumes / 编译 PDF」
- 「convert this docx to latex」
- 「dry-run apply for this job URL」
- 「check honesty boundaries on this bullet」

## What the agent should do

| Task | macOS / Linux | Windows (PowerShell) |
|------|---------------|----------------------|
| Compile all variants | `./build_resumes.sh` | `.\build_resumes.ps1` |
| Sample only | `cd resume_template && xelatex …` | `cd resume_template; xelatex …` |
| Convert formats | `python -m convert --input … --output …` | same |
| JD → variant | `python -m apply --jd-file … --dry-run` | same |
| Rehearse apply gate | `python -m apply … --rehearse` | same |
| Sync skill mirrors | `./scripts/sync_skills.sh` | `.\scripts\sync_skills.ps1` |
| Rules & checklist | `.cursor/skills/job-seeker/checklist.md` | same |

## Cursor vs WorkBuddy

| | Cursor | WorkBuddy |
|---|--------|-----------|
| Skill path | `.cursor/skills/job-seeker/` | `.workbuddy/skills/job-seeker/` |
| `agent_created` | Ignored | Set `true` for SkillManage |
| Portable mirror | `docs/skill/job-seeker/` | Copy from docs when exporting |

When updating the skill, edit **`docs/skill/job-seeker/`** first, then run:

- Windows: `.\scripts\sync_skills.ps1`
- macOS/Linux: `./scripts/sync_skills.sh`

See `docs/skill/job-seeker/README.md`.

## Privacy reminder

These stay **gitignored** — keep them only on your machine:

- `docs/experience_bank.md`, `docs/jd_mapping/`
- `LaTeX_Resume_CN/`, `LaTeX_Resume_EN/` (your real resumes)
- `outputs/*.pdf`, tracker CSV, `history/`

The public repo contains placeholders and the clean `resume_template/` only.

## Windows (Cursor on Windows)

- Build: `.\build_resumes.ps1` — full guide [`docs/BUILD_WINDOWS.md`](../BUILD_WINDOWS.md)
- Python venv: `.\.venv\Scripts\Activate.ps1`
- Apply env vars: `$env:JOB_SEEKER_NAME = "..."` (not `export`)
- Sync skills after edits: `.\scripts\sync_skills.ps1`
- Chinese Skill: `.cursor/skills/job-seeker/SKILL.zh-CN.md`
- Agent entry point: root [`AGENTS.md`](../AGENTS.md)
