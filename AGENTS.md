# Agent instructions (Codex / Cursor / WorkBuddy / compatible editors)

This repo ships a **project Skill** for resume workflows. Read it before editing
resumes, running apply, or changing skill mirrors.

| Resource | Path |
|----------|------|
| **Primary Skill (English)** | [`.cursor/skills/job-seeker/SKILL.md`](.cursor/skills/job-seeker/SKILL.md) |
| **Skill (中文)** | [`.cursor/skills/job-seeker/SKILL.zh-CN.md`](.cursor/skills/job-seeker/SKILL.zh-CN.md) |
| **Codex Skill** | [`.codex/skills/job-seeker/SKILL.md`](.codex/skills/job-seeker/SKILL.md) |
| Portable source (edit first) | [`docs/skill/job-seeker/`](docs/skill/job-seeker/) |
| Codex setup | [`docs/skill/CODEX.md`](docs/skill/CODEX.md) |
| Cursor setup | [`docs/skill/CURSOR.md`](docs/skill/CURSOR.md) |
| Checklist | [`.cursor/skills/job-seeker/checklist.md`](.cursor/skills/job-seeker/checklist.md) |

**Hard rules**

1. Read `docs/experience_bank.md` before changing resume bullets (copy from
   `docs/experience_bank.example.md` if missing).
2. Do not commit personal data (`outputs/`, `history/`, private `LaTeX_Resume_*`).
3. Do not auto-submit job applications — `apply` must stay human-in-the-loop.
4. After skill edits, run `scripts/sync_skills.ps1` (Windows) or
   `scripts/sync_skills.sh` (macOS/Linux).
5. Prefer existing CLI surfaces (`convert`, `apply`, build scripts) before adding
   a project MCP server.

**Build (platform)**

- Windows: `.\build_resumes.ps1` — see [`docs/BUILD_WINDOWS.md`](docs/BUILD_WINDOWS.md)
- macOS/Linux: `./build_resumes.sh` — see [`docs/BUILD_MAC.md`](docs/BUILD_MAC.md)
