# Using job-seeker with Codex

Codex reads the repo-level `AGENTS.md` automatically and can load the committed
project Skill from `.codex/skills/job-seeker/`. The portable source remains
`docs/skill/job-seeker/`; edit that first, then sync mirrors.

## Quick setup

1. Clone the repo and open it as the Codex workspace.
2. Copy private local material, but do not commit it:
   - `docs/experience_bank.example.md` -> `docs/experience_bank.md`
   - `resume_template/` -> `LaTeX_Resume_CN/` and/or `LaTeX_Resume_EN/`
3. Install platform tools:
   - Windows: MiKTeX with `xelatex`, Python 3.10+, optional pandoc
   - macOS / Linux: TeX Live with `xelatex`, Python 3.10+, optional pandoc
4. Install Python dependencies in a local virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   On macOS / Linux:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Suggested Codex prompts

- "Use $job-seeker to recommend a resume
  variant for this JD. Keep it dry-run only."
- "Check this resume bullet against the honesty boundaries before I use it."
- "Run the Windows build path and tell me whether the sample resume compiles."
- "Update the job-seeker Skill source, sync mirrors, and keep README user-facing."

## Operating rules for Codex

- Read `AGENTS.md` first, then `.codex/skills/job-seeker/SKILL.md` when the task
  touches resumes, conversion, apply, or Skill mirrors.
- Read `docs/experience_bank.md` before changing resume bullets. If it is
  missing, ask the user to create it from `docs/experience_bank.example.md`.
- Edit `docs/skill/job-seeker/` first when changing the Skill, then sync mirrors:

  ```powershell
  .\scripts\sync_skills.ps1
  ```

  On macOS / Linux:

  ```bash
  ./scripts/sync_skills.sh
  ```

- Keep applications human-in-the-loop. Use `python -m apply --dry-run` or
  `--rehearse` unless the user explicitly confirms a live action.
- Do not commit personal data from `outputs/`, `history/`, private resume
  folders, or the real experience bank.

## MCP status

This repo does not ship a project-specific MCP server yet. Prefer the existing
CLI surfaces first:

- `python -m convert` for format conversion
- `python -m apply --dry-run` or `--rehearse` for job application preparation
- `build_resumes.ps1` / `build_resumes.sh` for resume builds

Add an MCP server only when there is a stable external system to expose, such as
a private tracker database or a browser/session service that cannot be handled
through the current CLI.
