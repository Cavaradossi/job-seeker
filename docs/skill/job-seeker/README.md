# job-seeker Skill — Import & sync

Portable skill source: **`docs/skill/job-seeker/`**. Sync to editor-specific paths when you change the skill.

## Directory layout

```
docs/skill/job-seeker/          # Edit here first (portable / open-source source)
├── SKILL.md                    # English
├── SKILL.zh-CN.md              # 中文
├── references/
│   ├── master_prompt_extract.md
│   └── variant_playbook.md
├── checklist.md
└── README.md                     # this file

.cursor/skills/job-seeker/        # Cursor (committed — clone & open repo)
.workbuddy/skills/job-seeker/     # WorkBuddy (add agent_created: true in frontmatter)
```

## Codex

Codex uses the repo-level `AGENTS.md` as the agent entry point. Keep this
portable Skill as the source of truth, and see [`../CODEX.md`](../CODEX.md) for
Codex prompts, Windows setup notes, and the current MCP boundary.

## Cursor (recommended for this repo)

**No copy step needed** — `.cursor/skills/job-seeker/` is tracked in git. Open the
project in Cursor and invoke via natural language or `@job-seeker`.

Setup guide: [`../CURSOR.md`](../CURSOR.md).

## WorkBuddy

Project-level (travels with repo):

```bash
cp -r docs/skill/job-seeker/* .workbuddy/skills/job-seeker/
# Ensure frontmatter includes: agent_created: true
```

User-level: `cp -r docs/skill/job-seeker ~/.workbuddy/skills/job-seeker`

## Sync after edits

**Windows**

```powershell
.\scripts\sync_skills.ps1
```

**macOS / Linux**

```bash
chmod +x scripts/sync_skills.sh
./scripts/sync_skills.sh
```

## Validation (WorkBuddy)

If `skill-creator` is available:

```bash
python …/skill-creator/quick_validate.py .workbuddy/skills/job-seeker
```

`name` must match directory (`job-seeker`); only `[a-z0-9-]` in `name`.

## Placeholders

Examples use `YOUR_NAME`, `your-email@example.com`, `your-org/job-seeker` —
never real maintainer PII in the public repo.
