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
   (see root README and `docs/BUILD_MAC.md`).
5. `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

## How to invoke the skill

Cursor picks skills from the `description` field in frontmatter. You can also
steer explicitly:

- 「用申职器 Skill，根据这份 JD 改简历」
- 「compile resumes / 编译 PDF」
- 「convert this docx to latex」
- 「dry-run apply for this job URL」
- 「check honesty boundaries on this bullet」

## What the agent should do

| Task | Command / path |
|------|----------------|
| Compile all variants | `./build_resumes.sh` |
| Sample only | `cd resume_template && xelatex sample-resume-en_US-zh_CN.tex` |
| Convert formats | `python -m convert --input … --output …` |
| JD → variant | `python -m apply --jd-file … --dry-run` |
| Rehearse apply gate | `python -m apply … --rehearse` |
| Rules & checklist | `.cursor/skills/job-seeker/checklist.md` |

## Cursor vs WorkBuddy

| | Cursor | WorkBuddy |
|---|--------|-----------|
| Skill path | `.cursor/skills/job-seeker/` | `.workbuddy/skills/job-seeker/` |
| `agent_created` | Ignored | Set `true` for SkillManage |
| Portable mirror | `docs/skill/job-seeker/` | Copy from docs when exporting |

When updating the skill, edit **`docs/skill/job-seeker/`** first, then sync to
`.cursor/skills/` and `.workbuddy/skills/` (see `docs/skill/job-seeker/README.md`).

## Privacy reminder

These stay **gitignored** — keep them only on your machine:

- `docs/experience_bank.md`, `docs/jd_mapping/`
- `LaTeX_Resume_CN/`, `LaTeX_Resume_EN/` (your real resumes)
- `outputs/*.pdf`, tracker CSV, `history/`

The public repo contains placeholders and the clean `resume_template/` only.
