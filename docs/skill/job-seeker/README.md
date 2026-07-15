# job-seeker Skill — Import & sync

Portable skill source: **`docs/skill/job-seeker/`**. Sync to editor-specific paths when you change the skill.

## Directory layout

```
docs/skill/job-seeker/          # Edit here first (portable / open-source source)
├── SKILL.md
├── references/
│   ├── master_prompt_extract.md
│   └── variant_playbook.md
├── checklist.md
└── README.md                     # this file

.cursor/skills/job-seeker/        # Cursor (committed — clone & open repo)
.workbuddy/skills/job-seeker/     # WorkBuddy (add agent_created: true in frontmatter)
```

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

```bash
# From repo root (macOS / Linux)
cp docs/skill/job-seeker/SKILL.md .cursor/skills/job-seeker/SKILL.md
cp docs/skill/job-seeker/checklist.md .cursor/skills/job-seeker/checklist.md
cp -r docs/skill/job-seeker/references/* .cursor/skills/job-seeker/references/

cp docs/skill/job-seeker/SKILL.md .workbuddy/skills/job-seeker/SKILL.md
cp docs/skill/job-seeker/checklist.md .workbuddy/skills/job-seeker/checklist.md
# Then add agent_created: true to .workbuddy/skills/job-seeker/SKILL.md if overwritten
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
