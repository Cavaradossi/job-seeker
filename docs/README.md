# Documentation index

This is the map of everything under `docs/`. Start here, then jump to the file you need.
If you add a new document, **add a row to the table below** — that rule is enforced (see [`GOVERNANCE.md`](GOVERNANCE.md)).

## Guides

| Document | What it covers | Audience |
|----------|----------------|----------|
| [`BUILD_MAC.md`](BUILD_MAC.md) | TeX Live + pandoc on macOS/Linux | New users on Apple/Linux |
| [`BUILD_WINDOWS.md`](BUILD_WINDOWS.md) | MiKTeX + PowerShell on Windows | New users on Windows |
| [`job_seeker_opensource_plan.md`](job_seeker_opensource_plan.md) | Roadmap, phase breakdown, privacy strategy, and governance direction | Contributors |
| [`GOVERNANCE.md`](GOVERNANCE.md) | Rules that keep this repo (docs + file tree) from rotting | Contributors / maintainers |
| [`../scripts/README.md`](../scripts/README.md) | Skill sync scripts (`sync_skills.sh` / `.ps1`) | Contributors |

## Reference

| Document | What it covers | Audience |
|----------|----------------|----------|
| [`tracker_schema.md`](tracker_schema.md) | Column-by-column schema of the application tracker CSV | Anyone reading/writing the tracker |
| [`experience_bank.example.md`](experience_bank.example.md) | Template for your private experience bank (real one is gitignored) | Users tailoring resumes |

## Agent Skill

| Document | What it covers | Audience |
|----------|----------------|----------|
| [`skill/CODEX.md`](skill/CODEX.md) | Codex Skill setup, prompts, Windows notes, and MCP boundary | Codex users |
| [`skill/CURSOR.md`](skill/CURSOR.md) | Cursor setup — skill + rules + Windows notes | Cursor users |
| [`skill/job-seeker/SKILL.md`](skill/job-seeker/SKILL.md) | Agent Skill (English): workflow + honesty boundaries | AI editors |
| [`skill/job-seeker/SKILL.zh-CN.md`](skill/job-seeker/SKILL.zh-CN.md) | Agent Skill (中文) | Cursor / 中文对话 |
| [`skill/job-seeker/checklist.md`](skill/job-seeker/checklist.md) | Per-application checklist | AI editors |
| [`skill/job-seeker/references/`](skill/job-seeker/references/) | Master-prompt extract + variant playbook | AI editors |

---

## Where each kind of doc lives

- **User-facing overview** → root [`README.md`](../README.md) / [`README.zh-CN.md`](../README.zh-CN.md) (not here).
- **Per-package how-it-works** → the package's own `README.md` (`convert/README.md`, `apply/README.md`, `resume_template/README.md`) — kept next to the code it documents.
- **Cross-cutting guides, plans, schemas** → this `docs/` directory.

There is exactly one documentation directory: **`docs/`**. There is no `doc/`. See [`GOVERNANCE.md`](GOVERNANCE.md) for why and how that's enforced.
