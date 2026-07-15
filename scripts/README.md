# scripts/

Utility scripts for **job-seeker** (申职器). Not imported by `convert/` or `apply/`.

| Script | Platform | Purpose |
|--------|----------|---------|
| [`sync_skills.sh`](sync_skills.sh) | macOS / Linux | Copy `docs/skill/job-seeker/` → `.codex/skills/`, `.cursor/skills/`, and `.workbuddy/skills/`; add `agent_created: true` for WorkBuddy |
| [`sync_skills.ps1`](sync_skills.ps1) | Windows | Same as above (PowerShell) |

**When to run:** after editing anything under `docs/skill/job-seeker/` (SKILL, checklist, references).

Resume build scripts live at the repo root: [`build_resumes.sh`](../build_resumes.sh), [`build_resumes.ps1`](../build_resumes.ps1).
